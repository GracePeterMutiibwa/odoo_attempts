{
    'name': 'Purchase Request Addon',
    'author': 'Grace Peter Mutiibwa',
    'version': '1.0',
    'depends': ['product', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request_view.xml'
    ],
    'installable': True,
    'license': 'LGPL-3'
}