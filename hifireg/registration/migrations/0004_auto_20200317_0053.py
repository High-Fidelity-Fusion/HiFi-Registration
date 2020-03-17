# Generated by Django 3.0.4 on 2020-03-17 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_apfund'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('section', models.CharField(choices=[('DANCE', 'Dance Passes'), ('CLASS', 'Class Passes'), ('ADDON', 'Add-Ons')], max_length=5)),
            ],
        ),
        migrations.RenameField(
            model_name='order',
            old_name='final_price',
            new_name='accessible_price',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='original_unit_price',
            new_name='unit_price',
        ),
        migrations.AddField(
            model_name='order',
            name='original_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='total_price',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_ap_eligible',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_compable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='comp_code',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.CreateModel(
            name='ProductCategorySlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_exclusionary', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registration.ProductCategory')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='category_slots',
            field=models.ManyToManyField(to='registration.ProductCategorySlot'),
        ),
    ]
