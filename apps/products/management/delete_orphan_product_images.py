from __future__ import annotations

from dataclasses import dataclass

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.products.models import Product, ProductImage


@dataclass
class Stats:
    checked: int = 0
    deleted: int = 0
    skipped: int = 0
    failed: int = 0


class Command(BaseCommand):
    help = (
        "Delete ProductImage records whose product_id has no matching Product "
        "(orphan product images)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show orphan product images without deleting anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        stats = Stats()

        self.stdout.write(self.style.NOTICE("Scanning for orphan ProductImage rows..."))

        queryset = ProductImage.objects.exclude(
            product_id__in=Product.objects.values("id")
        )

        for obj in queryset.iterator():
            stats.checked += 1

            if dry_run:
                stats.skipped += 1
                self.stdout.write(
                    self.style.NOTICE(
                        f"[DRY-RUN] Would delete ProductImage#{obj.pk} (product_id={obj.product_id})"
                    )
                )
                continue

            try:
                self._delete_file(obj, "image")
                self._delete_file(obj, "image_desktop")
                # Keep compatibility with older schema where image_mobile may exist.
                self._delete_file(obj, "image_mobile")

                obj.delete()
                stats.deleted += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted ProductImage#{obj.pk} (product_id={obj.product_id})"
                    )
                )
            except Exception as exc:
                stats.failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to delete ProductImage#{obj.pk} (product_id={obj.product_id}): {exc}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Done. checked={checked}, deleted={deleted}, dry_run_skipped={skipped}, failed={failed}".format(
                    checked=stats.checked,
                    deleted=stats.deleted,
                    skipped=stats.skipped,
                    failed=stats.failed,
                )
            )
        )

    @staticmethod
    def _delete_file(obj: ProductImage, attr: str) -> None:
        if not hasattr(obj, attr):
            return

        field_file = getattr(obj, attr)
        if not field_file or not getattr(field_file, "name", None):
            return

        file_name = field_file.name
        if default_storage.exists(file_name):
            default_storage.delete(file_name)
