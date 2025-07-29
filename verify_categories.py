#!/usr/bin/env python
"""
Script to verify the category structure in the Arabic ArXiv database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from main.models import MainCategory, Category

def display_categories():
    """Display all main categories and their subcategories"""
    print("=" * 60)
    print("ARABIC ARXIV - CATEGORY STRUCTURE")
    print("=" * 60)
    
    main_categories = MainCategory.objects.all().order_by('id')
    
    for i, main_cat in enumerate(main_categories, 1):
        print(f"\n{i}. {main_cat.name}")
        print(f"   ({main_cat.english_name})")
        print("-" * 40)
        
        subcategories = main_cat.categories.all().order_by('name')
        for j, sub_cat in enumerate(subcategories, 1):
            print(f"   {j}. {sub_cat.name}")
    
    print("\n" + "=" * 60)
    print(f"Total: {MainCategory.objects.count()} main categories")
    print(f"Total: {Category.objects.count()} subcategories")
    print("=" * 60)

def test_category_usage():
    """Test how categories can be used in forms and queries"""
    print("\n" + "=" * 60)
    print("CATEGORY USAGE EXAMPLES")
    print("=" * 60)
    
    # Example 1: Get all subcategories for a specific main category
    computer_science = MainCategory.objects.get(english_name='Computer Science and Technology')
    print(f"\n1. All subcategories under '{computer_science.name}':")
    for cat in computer_science.categories.all():
        print(f"   - {cat.name}")
    
    # Example 2: Get main category for a specific subcategory
    ai_category = Category.objects.get(name='الذكاء الاصطناعي')
    print(f"\n2. Main category for 'الذكاء الاصطناعي': {ai_category.main_category.name}")
    
    # Example 3: Count posts in each main category (if any exist)
    print(f"\n3. Posts count by main category:")
    for main_cat in MainCategory.objects.all():
        total_posts = sum(cat.posts.count() for cat in main_cat.categories.all())
        print(f"   {main_cat.name}: {total_posts} posts")

if __name__ == "__main__":
    display_categories()
    test_category_usage() 