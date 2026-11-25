"""Explicitly fictional inventory for presentation and automated acceptance tests."""


def example_vehicles():
    return [
        {'make':'Showcase','model':'City Hybrid','year':2022,'price':2350000,'mileage':42000,'availability':'available',
         'body_style':'sedan','fuel_type':'hybrid','drivetrain':'fwd','transmission':'automatic','seats':5,
         'mpg_combined':44,'cargo_cubic_feet':15,'features':['Rear camera','Heated seats'],'synthetic':True},
        {'make':'Showcase','model':'Family SUV','year':2021,'price':2650000,'mileage':38000,'availability':'available',
         'body_style':'suv','fuel_type':'gasoline','drivetrain':'awd','transmission':'automatic','seats':7,
         'mpg_combined':25,'cargo_cubic_feet':38,'features':['Third row','Rear camera'],'synthetic':True},
        {'make':'Showcase','model':'Compact Hatch','year':2020,'price':1890000,'mileage':58000,'availability':'available',
         'body_style':'hatchback','fuel_type':'gasoline','drivetrain':'fwd','transmission':'automatic','seats':5,
         'mpg_combined':34,'cargo_cubic_feet':22,'features':['Rear camera'],'synthetic':True},
        {'make':'Showcase','model':'Utility AWD','year':2022,'price':2490000,'mileage':46000,'availability':'available',
         'body_style':'suv','fuel_type':'gasoline','drivetrain':'awd','transmission':'automatic','seats':5,
         'mpg_combined':None,'cargo_cubic_feet':None,'features':['Roof rails'],'synthetic':True},
    ]
