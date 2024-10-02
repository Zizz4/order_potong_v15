{
    'name': 'SDL Order Potong',
    'version': '15.0',
    'summary': 'SDL Order Potong',
    'description': 'SDL Order Potong',
    'category': 'Category',
    'author': 'Muhamad Syahril Aziz',
    'license': 'LGPL-3',
    'depends': ['stock', 'purchase'],
    'data': ['security/ir.model.access.csv',

             'wizard/sdl_order_potong_create_po.xml',

             'views/sdl_order_potong.xml',
             'views/sdl_order_potong_po.xml',

             'data/sdl_order_potong_seq.xml',
             'data/stock_picking_type.xml',
             ],
    'installable': True,
    'auto_install': False
}
