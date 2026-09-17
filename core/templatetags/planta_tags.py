from django import template

register = template.Library()

ICONS = {
    'ornamental': 'fa-spa',
    'medicinal':  'fa-mortar-pestle',
    'fruteira':   'fa-apple-whole',
    'aromatica':  'fa-wind',
}

@register.filter
def planta_icon(categoria):
    return ICONS.get(str(categoria).lower(), 'fa-seedling')

@register.simple_tag
def cat_icon(categoria):
    icon = ICONS.get(str(categoria).lower(), 'fa-seedling')
    return f'<i class="fas {icon}"></i>'
