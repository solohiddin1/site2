# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AppBanner(models.Model):

    class Meta:
        managed = False
        db_table = 'app_banner'


class AppBannerTranslation(models.Model):
    language_code = models.CharField(max_length=15)
    name = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=100)
    alt = models.CharField(max_length=255, blank=True, null=True)
    master = models.ForeignKey(AppBanner, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_banner_translation'
        unique_together = (('language_code', 'master'),)


class AppCategory(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    image = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_category'


class AppCategoryTranslation(models.Model):
    language_code = models.CharField(max_length=15)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    master = models.ForeignKey(AppCategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_category_translation'
        unique_together = (('language_code', 'master'),)


class AppCertificates(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    image = models.CharField(max_length=100)
    ordering = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'app_certificates'


class AppCity(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'app_city'


class AppCompany(models.Model):
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=254)
    website = models.CharField(max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_company'


class AppCompanyTranslation(models.Model):
    language_code = models.CharField(max_length=15)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    about_us = models.TextField()
    master = models.ForeignKey(AppCompany, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_company_translation'
        unique_together = (('language_code', 'master'),)


class AppPartners(models.Model):
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'app_partners'


class AppProduct(models.Model):
    sku = models.CharField(unique=True, max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    category = models.ForeignKey(AppCategory, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_product'


class AppProductTranslation(models.Model):
    language_code = models.CharField(max_length=15)
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.CharField(max_length=255, blank=True, null=True)
    master = models.ForeignKey(AppProduct, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_product_translation'
        unique_together = (('language_code', 'master'),)


class AppProductimage(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    image = models.CharField(max_length=100)
    alt = models.CharField(max_length=255)
    ordering = models.PositiveIntegerField()
    product = models.ForeignKey(AppProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'app_productimage'


class AppServicecenterdescription(models.Model):

    class Meta:
        managed = False
        db_table = 'app_servicecenterdescription'


class AppServicecenterdescriptionTranslation(models.Model):
    language_code = models.CharField(max_length=15)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    master = models.ForeignKey(AppServicecenterdescription, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_servicecenterdescription_translation'
        unique_together = (('language_code', 'master'),)


class AppServicelocation(models.Model):
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=254, blank=True, null=True)
    map_url = models.CharField(max_length=2000, blank=True, null=True)
    city = models.OneToOneField(AppCity, models.DO_NOTHING)
    description = models.ForeignKey(AppServicecenterdescription, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'app_servicelocation'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
