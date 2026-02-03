from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.template.response import TemplateResponse
from django.db.models import Q
from django.http import HttpResponse 
from .models import Category, Brand, Product

class IndexView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/home_content.html', context)
        return TemplateResponse(request, self.template_name, context)


class CatalogView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        category_slug = kwargs.get('category_slug')
        brand_slug = kwargs.get('brand_slug') or self.request.GET.get('brand')
        category_from_get = self.request.GET.get('category')
        query = self.request.GET.get('q')

        products = Product.objects.all().order_by('-created_at')
        current_category = None
        current_brand = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)
        elif category_from_get:
            current_category = get_object_or_404(Category, slug=category_from_get)
            products = products.filter(category=current_category)

        if brand_slug:
            current_brand = get_object_or_404(Brand, slug=brand_slug)
            products = products.filter(brand=current_brand)

        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        context.update({
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'products': products,
            'current_category': current_category,
            'current_brand': current_brand,
            'category_from_get': category_from_get, 
            'search_query': query or ''
        })
        return context

    def get(self, request, *args, **kwargs):
        # 1. Если нажали крестик "сброс" - возвращаем ТОЛЬКО кнопку ПОИСК
        if request.headers.get('HX-Request') and request.GET.get('reset_search') == 'true':
            return HttpResponse('''
                <button hx-get="/catalog/?show_search=true" 
                        hx-target="#search-slot" 
                        hx-swap="innerHTML" 
                        class="text-sm font-medium uppercase hover:text-gray-300 transition-colors">ПОИСК</button>
            ''')

        context = self.get_context_data(**kwargs)
        
        # 2. Обработка HTMX запросов
        if request.headers.get('HX-Request'):
            # Показать поле ввода поиска
            if request.GET.get('show_search') == 'true':
                return TemplateResponse(request, 'main/search_input.html', context)
            
            # Показать модалку фильтров
            if request.GET.get('show_filters') == 'true':
                return TemplateResponse(request, 'main/filter_modal.html', context)
            
            # В остальном - отдаем контент каталога (результаты поиска или категории)
            return TemplateResponse(request, 'main/catalog.html', context)
        
        # 3. Обычный запрос (не HTMX)
        return TemplateResponse(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/base.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:5]
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/product_detail.html', context)
        return TemplateResponse(request, self.template_name, context)
    

class AboutView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['is_about'] = True 
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/about.html', context)
        return TemplateResponse(request, self.template_name, context)
    

class PriceListView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['is_price_list'] = True 
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/price_list.html', context)
        return TemplateResponse(request, self.template_name, context)