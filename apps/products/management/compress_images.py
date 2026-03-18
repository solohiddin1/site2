from __future__ import annotations

from dataclasses import dataclass

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.categories.models import Category, SubCategory
from apps.products.models import ProductImage
from apps.products.utils import compress_image


@dataclass
class Stats:
	checked: int = 0
	compressed: int = 0
	skipped: int = 0
	failed: int = 0


class Command(BaseCommand):
	help = (
		"Compress missing image derivatives for ProductImage, Category, and SubCategory "
		"when original file exists in both DB field and storage."
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--dry-run",
			action="store_true",
			help="Show what would be compressed without writing files.",
		)

	def handle(self, *args, **options):
		dry_run = options["dry_run"]
		stats = Stats()

		self.stdout.write(self.style.NOTICE("Starting compression backfill..."))

		self._process_queryset(
			queryset=ProductImage.objects.filter(image__isnull=False).exclude(image=""),
			original_attr="image",
			compressed_attr="image_desktop",
			label="ProductImage.image -> image_desktop",
			stats=stats,
			dry_run=dry_run,
		)

		self._process_queryset(
			queryset=Category.objects.filter(image__isnull=False).exclude(image=""),
			original_attr="image",
			compressed_attr="image_compressed",
			label="Category.image -> image_compressed",
			stats=stats,
			dry_run=dry_run,
		)

		self._process_queryset(
			queryset=Category.objects.filter(second_image__isnull=False).exclude(second_image=""),
			original_attr="second_image",
			compressed_attr="second_image_compressed",
			label="Category.second_image -> second_image_compressed",
			stats=stats,
			dry_run=dry_run,
		)

		self._process_queryset(
			queryset=SubCategory.objects.filter(image__isnull=False).exclude(image=""),
			original_attr="image",
			compressed_attr="image_compressed",
			label="SubCategory.image -> image_compressed",
			stats=stats,
			dry_run=dry_run,
		)

		summary_style = self.style.WARNING if stats.failed else self.style.SUCCESS
		self.stdout.write(
			summary_style(
				"Done. checked={checked}, compressed={compressed}, skipped={skipped}, failed={failed}".format(
					checked=stats.checked,
					compressed=stats.compressed,
					skipped=stats.skipped,
					failed=stats.failed,
				)
			)
		)

	def _process_queryset(
		self,
		queryset,
		original_attr: str,
		compressed_attr: str,
		label: str,
		stats: Stats,
		dry_run: bool,
	):
		self.stdout.write(self.style.NOTICE(f"Processing {label}..."))

		for obj in queryset.iterator():
			stats.checked += 1

			original = getattr(obj, original_attr, None)
			compressed = getattr(obj, compressed_attr, None)

			if not original or not getattr(original, "name", None):
				stats.skipped += 1
				continue

			if not default_storage.exists(original.name):
				stats.skipped += 1
				self.stdout.write(
					self.style.WARNING(
						f"Skipping {type(obj).__name__}#{obj.pk}: original file missing in storage ({original.name})"
					)
				)
				continue

			compressed_exists = bool(
				compressed and getattr(compressed, "name", None) and default_storage.exists(compressed.name)
			)
			if compressed_exists:
				stats.skipped += 1
				continue

			if dry_run:
				stats.compressed += 1
				self.stdout.write(
					self.style.NOTICE(
						f"[DRY-RUN] Would compress {type(obj).__name__}#{obj.pk}: {original_attr} -> {compressed_attr}"
					)
				)
				continue

			try:
				content = compress_image(
					original,
					sizes=None,
					format="WEBP",
					quality=82,
					keep_dimensions=True,
				)
				getattr(obj, compressed_attr).save(content.name, content, save=False)
				type(obj).objects.filter(pk=obj.pk).update(
					**{compressed_attr: getattr(obj, compressed_attr)}
				)

				stats.compressed += 1
				self.stdout.write(
					self.style.SUCCESS(
						f"Compressed {type(obj).__name__}#{obj.pk}: {original_attr} -> {compressed_attr}"
					)
				)
			except Exception as exc:
				stats.failed += 1
				self.stdout.write(
					self.style.ERROR(
						f"Failed {type(obj).__name__}#{obj.pk}: {original_attr} -> {compressed_attr} ({exc})"
					)
				)
