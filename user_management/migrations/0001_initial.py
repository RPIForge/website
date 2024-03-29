

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rin', models.PositiveIntegerField(blank=True, default=None, null=True, unique=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer Not to Say')], default='', max_length=255)),
                ('major', models.CharField(blank=True, choices=[('aeronautical_engineering', 'Aeronautical Engineering'), ('applied_physics', 'Applied Physics'), ('architectural_sciences', 'Architectural Sciences'), ('architecture', 'Architecture'), ('astronomy', 'Astronomy'), ('biochemistry_and_biophysics', 'Biochemistry and Biophysics'), ('bioinformatics_and_molecular_biology', 'Bioinformatics and Molecular Biology'), ('biology', 'Biology'), ('biomedical_engineering', 'Biomedical Engineering'), ('building_science', 'Building Science'), ('business_analytics', 'Business Analytics'), ('business_and_management', 'Business and Management'), ('chemical_engineering', 'Chemical Engineering'), ('chemistry', 'Chemistry'), ('civil_engineering', 'Civil Engineering'), ('cognitive_science', 'Cognitive Science'), ('communication_and_rhetoric', 'Communication and Rhetoric'), ('communication_media_and_design', 'Communication, Media, and Design'), ('computer_and_systems_engineering', 'Computer and Systems Engineering'), ('computer_science', 'Computer Science'), ('decision_sciences_and_engineering_systems', 'Decision Sciences and Engineering Systems'), ('design_innovation_and_society', 'Design, Innovation, and Society'), ('economics', 'Economics'), ('electrical_engineering', 'Electrical Engineering'), ('electronic_arts', 'Electronic Arts'), ('environmental_engineering', 'Environmental Engineering'), ('environmental_science', 'Environmental Science'), ('games_and_simulation_arts_and_sciences', 'Games and Simulation Arts and Sciences'), ('geology', 'Geology'), ('hydrogeology', 'Hydrogeology'), ('industrial_and_management_engineering', 'Industrial and Management Engineering'), ('information_technology', 'Information Technology'), ('lighting', 'Lighting'), ('management', 'Management'), ('materials_engineering', 'Materials Engineering'), ('mathematics', 'Mathematics'), ('mathematics_(applied)', 'Mathematics (Applied)'), ('mechanical_engineering', 'Mechanical Engineering'), ('multidisciplinary_science', 'Multidisciplinary Science'), ('music', 'Music'), ('nuclear_engineering', 'Nuclear Engineering'), ('nuclear_engineering_and_science', 'Nuclear Engineering and Science'), ('philosophy', 'Philosophy'), ('physics', 'Physics'), ('psychological_science', 'Psychological Science'), ('quantitative_finance_and_risk_analytics', 'Quantitative Finance and Risk Analytics'), ('science_and_technology_studies', 'Science and Technology Studies'), ('science_technology_and_society', 'Science, Technology, and Society'), ('supply_chain_management', 'Supply Chain Management'), ('sustainability_studies', 'Sustainability Studies'), ('systems_engineering_and_technology_management', 'Systems Engineering and Technology Management'), ('technology_commercialization_and_entrepreneurship', 'Technology, Commercialization, and Entrepreneurship'), ('transportation_engineering', 'Transportation Engineering')], default='', max_length=255)),
                ('is_active', models.BooleanField(default=False)),
                ('is_graduating', models.BooleanField(default=False)),
                ('anonymous_usages', models.BooleanField(default=False)),
                ('email_verification_token', models.CharField(blank=True, default='', max_length=255, unique=True)),
                ('entertainment_mode', models.BooleanField(default=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_management_userprofile',
            },
        ),
    ]
