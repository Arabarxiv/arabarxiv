from django.core.management.base import BaseCommand
from main.models import MainCategory, Category


class Command(BaseCommand):
    help = 'Populate the database with main categories and subcategories for academic research'

    def handle(self, *args, **options):
        self.stdout.write('Creating main categories and subcategories...')
        
        # Clear existing categories
        Category.objects.all().delete()
        MainCategory.objects.all().delete()
        
        # 1. العلوم الطبيعية والرياضيات (Natural Sciences and Mathematics)
        natural_sciences = MainCategory.objects.create(
            name='العلوم الطبيعية والرياضيات',
            english_name='Natural Sciences and Mathematics'
        )
        
        Category.objects.bulk_create([
            Category(main_category=natural_sciences, name='الرياضيات'),
            Category(main_category=natural_sciences, name='الفيزياء'),
            Category(main_category=natural_sciences, name='الكيمياء'),
            Category(main_category=natural_sciences, name='علم الأحياء'),
            Category(main_category=natural_sciences, name='علم الفلك'),
            Category(main_category=natural_sciences, name='علوم الأرض'),
            Category(main_category=natural_sciences, name='علم المواد'),
            Category(main_category=natural_sciences, name='الإحصاء'),
        ])
        
        # 2. علوم الحاسوب والتكنولوجيا (Computer Science and Technology)
        computer_science = MainCategory.objects.create(
            name='علوم الحاسوب والتكنولوجيا',
            english_name='Computer Science and Technology'
        )
        
        Category.objects.bulk_create([
            Category(main_category=computer_science, name='الذكاء الاصطناعي'),
            Category(main_category=computer_science, name='علم البيانات'),
            Category(main_category=computer_science, name='أمن المعلومات'),
            Category(main_category=computer_science, name='تطوير البرمجيات'),
            Category(main_category=computer_science, name='الشبكات والاتصالات'),
            Category(main_category=computer_science, name='قواعد البيانات'),
            Category(main_category=computer_science, name='الحوسبة السحابية'),
            Category(main_category=computer_science, name='إنترنت الأشياء'),
            Category(main_category=computer_science, name='الواقع الافتراضي'),
        ])
        
        # 3. العلوم الطبية والصحية (Medical and Health Sciences)
        medical_sciences = MainCategory.objects.create(
            name='العلوم الطبية والصحية',
            english_name='Medical and Health Sciences'
        )
        
        Category.objects.bulk_create([
            Category(main_category=medical_sciences, name='الطب البشري'),
            Category(main_category=medical_sciences, name='طب الأسنان'),
            Category(main_category=medical_sciences, name='الصيدلة'),
            Category(main_category=medical_sciences, name='التمريض'),
            Category(main_category=medical_sciences, name='الصحة العامة'),
            Category(main_category=medical_sciences, name='علم النفس'),
            Category(main_category=medical_sciences, name='العلاج الطبيعي'),
            Category(main_category=medical_sciences, name='التغذية'),
            Category(main_category=medical_sciences, name='علم الأوبئة'),
        ])
        
        # 4. العلوم الاجتماعية والإنسانية (Social Sciences and Humanities)
        social_sciences = MainCategory.objects.create(
            name='العلوم الاجتماعية والإنسانية',
            english_name='Social Sciences and Humanities'
        )
        
        Category.objects.bulk_create([
            Category(main_category=social_sciences, name='علم الاجتماع'),
            Category(main_category=social_sciences, name='علم النفس الاجتماعي'),
            Category(main_category=social_sciences, name='الاقتصاد'),
            Category(main_category=social_sciences, name='العلوم السياسية'),
            Category(main_category=social_sciences, name='التاريخ'),
            Category(main_category=social_sciences, name='الجغرافيا'),
            Category(main_category=social_sciences, name='اللغة العربية'),
            Category(main_category=social_sciences, name='اللغة الإنجليزية'),
            Category(main_category=social_sciences, name='الفلسفة'),
            Category(main_category=social_sciences, name='علم الآثار'),
            Category(main_category=social_sciences, name='التربية والتعليم'),
        ])
        
        # 5. الهندسة والعمارة (Engineering and Architecture)
        engineering = MainCategory.objects.create(
            name='الهندسة والعمارة',
            english_name='Engineering and Architecture'
        )
        
        Category.objects.bulk_create([
            Category(main_category=engineering, name='الهندسة المدنية'),
            Category(main_category=engineering, name='الهندسة الميكانيكية'),
            Category(main_category=engineering, name='الهندسة الكهربائية'),
            Category(main_category=engineering, name='الهندسة الكيميائية'),
            Category(main_category=engineering, name='الهندسة الصناعية'),
            Category(main_category=engineering, name='الهندسة المعمارية'),
            Category(main_category=engineering, name='هندسة الطيران'),
            Category(main_category=engineering, name='الهندسة البيئية'),
            Category(main_category=engineering, name='هندسة المواد'),
            Category(main_category=engineering, name='الهندسة الطبية الحيوية'),
        ])
        
        # 6. العلوم الزراعية والبيئية (Agricultural and Environmental Sciences)
        agricultural_sciences = MainCategory.objects.create(
            name='العلوم الزراعية والبيئية',
            english_name='Agricultural and Environmental Sciences'
        )
        
        Category.objects.bulk_create([
            Category(main_category=agricultural_sciences, name='الزراعة'),
            Category(main_category=agricultural_sciences, name='علوم البيئة'),
            Category(main_category=agricultural_sciences, name='الغابات'),
            Category(main_category=agricultural_sciences, name='تربية الحيوان'),
            Category(main_category=agricultural_sciences, name='علم التربة'),
            Category(main_category=agricultural_sciences, name='تكنولوجيا الأغذية'),
            Category(main_category=agricultural_sciences, name='المصايد'),
            Category(main_category=agricultural_sciences, name='التنمية المستدامة'),
        ])
        
        # 7. إدارة الأعمال والاقتصاد (Business and Economics)
        business = MainCategory.objects.create(
            name='إدارة الأعمال والاقتصاد',
            english_name='Business and Economics'
        )
        
        Category.objects.bulk_create([
            Category(main_category=business, name='إدارة الأعمال'),
            Category(main_category=business, name='المحاسبة'),
            Category(main_category=business, name='التمويل'),
            Category(main_category=business, name='التسويق'),
            Category(main_category=business, name='الاقتصاد الإسلامي'),
            Category(main_category=business, name='إدارة الموارد البشرية'),
            Category(main_category=business, name='ريادة الأعمال'),
            Category(main_category=business, name='الاقتصاد الدولي'),
        ])
        
        # 8. القانون والدراسات القانونية (Law and Legal Studies)
        law = MainCategory.objects.create(
            name='القانون والدراسات القانونية',
            english_name='Law and Legal Studies'
        )
        
        Category.objects.bulk_create([
            Category(main_category=law, name='القانون المدني'),
            Category(main_category=law, name='القانون الجنائي'),
            Category(main_category=law, name='القانون التجاري'),
            Category(main_category=law, name='القانون الدولي'),
            Category(main_category=law, name='القانون الدستوري'),
            Category(main_category=law, name='القانون الإداري'),
            Category(main_category=law, name='الشريعة الإسلامية'),
            Category(main_category=law, name='حقوق الإنسان'),
        ])
        
        # 9. الفنون والتصميم (Arts and Design)
        arts = MainCategory.objects.create(
            name='الفنون والتصميم',
            english_name='Arts and Design'
        )
        
        Category.objects.bulk_create([
            Category(main_category=arts, name='الفنون البصرية'),
            Category(main_category=arts, name='التصميم الجرافيكي'),
            Category(main_category=arts, name='التصميم الصناعي'),
            Category(main_category=arts, name='العمارة الداخلية'),
            Category(main_category=arts, name='الموسيقى'),
            Category(main_category=arts, name='المسرح'),
            Category(main_category=arts, name='السينما'),
            Category(main_category=arts, name='التصوير الفوتوغرافي'),
        ])
        
        # 10. الدراسات الإسلامية والشرقية (Islamic and Oriental Studies)
        islamic_studies = MainCategory.objects.create(
            name='الدراسات الإسلامية والشرقية',
            english_name='Islamic and Oriental Studies'
        )
        
        Category.objects.bulk_create([
            Category(main_category=islamic_studies, name='علوم القرآن'),
            Category(main_category=islamic_studies, name='علوم الحديث'),
            Category(main_category=islamic_studies, name='الفقه الإسلامي'),
            Category(main_category=islamic_studies, name='العقيدة الإسلامية'),
            Category(main_category=islamic_studies, name='التاريخ الإسلامي'),
            Category(main_category=islamic_studies, name='الحضارة الإسلامية'),
            Category(main_category=islamic_studies, name='الدراسات الشرقية'),
            Category(main_category=islamic_studies, name='اللغة العربية وآدابها'),
        ])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {MainCategory.objects.count()} main categories and {Category.objects.count()} subcategories!'
            )
        )
        
        # Display the created categories
        self.stdout.write('\nCreated Main Categories:')
        for main_cat in MainCategory.objects.all():
            self.stdout.write(f'  - {main_cat.name} ({main_cat.english_name})')
            for sub_cat in main_cat.categories.all():
                self.stdout.write(f'    * {sub_cat.name}')
            self.stdout.write('') 