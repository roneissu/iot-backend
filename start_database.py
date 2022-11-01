from app.database import DeviceType, db

db.create_all()

dev_types = [
    'glucometer',
    'health',
    'nebulizer',
    'oximeter',
    'pill dispenser',
    'sphygmomanometer',
    'thermometer'
]

for t in dev_types:
    dev_type = DeviceType()
    dev_type.name = t
    db.session.add(dev_type)
    db.session.commit()