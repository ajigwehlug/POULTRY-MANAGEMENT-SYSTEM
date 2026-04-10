{
    'name': 'Poultry Management System',
    'version': '1.0.0',
    'category': 'Inventory/Livestock',
    'author': 'Odoo Ghana',
    'website': 'https://github.com/ajigwehlugodoo/poultry-ms',
    'summary': 'Complete Poultry Farming Management with Manufacturing & Accounting Integration',
    'description': '''
        Comprehensive Poultry Management System for Ghana
        
        Features:
        - Farm and flock management
        - Daily operations tracking with auto journal entries
        - Manufacturing orders for slaughtering, egg processing
        - Integration with Odoo Sales, Accounting, CRM, and Inventory
        - Complete financial reporting and traceability
        - Work center tracking and quality control
        - Byproduct management (feathers, offal)
        - Multi-product support (broilers, layers, eggs)
    ''',
    'depends': [
        'base',
        'mail',
        'sale',
        'account',
        'mrp',
        'stock',
        'crm',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/farm_views.xml',
        'views/flock_views.xml',
        'views/operations_views.xml',
        'views/manufacturing_views.xml',
        'views/menu.xml',
        'data/accounts.xml',
        'data/locations.xml',
        'data/products.xml',
    ],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [],
    },
}
