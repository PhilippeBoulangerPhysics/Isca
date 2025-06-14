import os

import numpy as np

from isca import IscaCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

from Isca.exp.test_cases.bucket_hydrology.field_table_write import write_ft

NCORES = 32

RESOLUTION = "T42", 25

base_dir = os.path.dirname(os.path.realpath(__file__))
# a CodeBase can be a directory on the computer,
# useful for iterative development
cb = IscaCodeBase.from_directory(GFDL_BASE)

# or it can point to a specific git repo and commit id.
# This method should ensure future, independent, reproducibility of results.
# cb = DryCodeBase.from_repo(repo='https://github.com/isca/isca', commit='isca1.1')

# compilation depends on computer specific settings.  The $GFDL_ENV
# environment variable is used to determine which `$GFDL_BASE/src/extra/env` file
# is used to load the correct compilers.  The env file is always loaded from
# $GFDL_BASE and not the checked out git repo.

cb.compile(debug = False)  # compile the source code to working directory $GFDL_WORK/codebase

n_moments = 4

field_table_name = "field_table_age_" + str(n_moments)
write_ft(field_table_name,n_moments)

# Write field table

# create an Experiment object to handle the configuration of model parameters
# and output diagnostics
exp = Experiment(name = 'fr_T42_4mom_continents',ext_field_table=field_table_name, codebase=cb)

exp.inputfiles = ['./input/era_land_T42.nc']

#Tell model how to write diagnostics
diag = DiagTable()
diag.add_file('atmos_monthly', 6, 'hours', time_units='days')

#Tell model which diagnostics to write

diag.add_field('dynamics', 'ps', time_avg=True)
diag.add_field('dynamics', 'bk')
diag.add_field('dynamics', 'pk')
diag.add_field('atmosphere', 'precipitation', time_avg=True)
diag.add_field('mixed_layer', 't_surf', time_avg=True)
diag.add_field('mixed_layer', 'flux_lhe', time_avg=True)
diag.add_field('mixed_layer', 'flux_t', time_avg=True)
diag.add_field('mixed_layer', 'flux_oceanq', time_avg=True)
diag.add_field('mixed_layer', 'corr_flux', time_avg=True)

diag.add_field('dynamics', 'sphum', time_avg=True)
diag.add_field('dynamics', 'ucomp', time_avg=True)
diag.add_field('dynamics', 'vcomp', time_avg=True)
diag.add_field('dynamics', 'omega', time_avg=True)
diag.add_field('dynamics', 'wspd', time_avg=True)
"""diag.add_field('dynamics', 'height', time_avg=True)
diag.add_field('dynamics', 'temp', time_avg=True)
diag.add_field('dynamics', 'vor', time_avg=True)
diag.add_field('dynamics', 'div', time_avg=True)

diag.add_field('two_stream', 'olr', time_avg=True)
diag.add_field('two_stream', 'swdn_sfc', time_avg=True)
diag.add_field('two_stream', 'swdn_toa', time_avg=True)
diag.add_field('two_stream', 'lwup_sfc', time_avg=True)
diag.add_field('two_stream', 'lwdn_sfc', time_avg=True)
diag.add_field('two_stream', 'net_lw_surf', time_avg=True)
diag.add_field('two_stream', 'flux_rad', time_avg=True)
diag.add_field('two_stream', 'flux_lw', time_avg=True)
diag.add_field('two_stream', 'flux_sw', time_avg=True)"""


diag.add_field('vert_turb', 'z_pbl', time_avg=True)

for ind in range(n_moments):
    name = f"sphum_age_{ind+1}"
    diag.add_field('dynamics', name, time_avg=True)

diag.add_field('atmosphere', 'cape', time_avg=True)
diag.add_field('atmosphere', 'dt_qg_convection', time_avg=True)
diag.add_field('atmosphere', 'dt_qg_condensation', time_avg=True)
diag.add_field('atmosphere', 'dt_sink', time_avg=True)
diag.add_field('atmosphere', 'dt_qg_diffusion', time_avg=True)
diag.add_field('atmosphere', 'rh', time_avg=True)

exp.diag_table = diag

#Empty the run directory ready to run
exp.clear_rundir()

#Define values for the 'core' namelist
exp.namelist = namelist = Namelist({
    'main_nml':{
     'days'   : 30,
     'hours'  : 0,
     'minutes': 0,
     'seconds': 0,
     'dt_atmos':720,
     'current_date' : [1,1,1,0,0,0],
     'calendar' : 'thirty_day'
    },

    'idealized_moist_phys_nml': {
        'do_damping': True,
        'turb':True,
        'mixed_layer_bc':True,
        'floor_evap' : False,
        'do_virtual' :False,
        'do_simple': True,
        'roughness_mom':3.21e-05,
        'roughness_heat':3.21e-05,
        'roughness_moist':3.21e-05,                
        'two_stream_gray': True,     #Use grey radiation
         'land_option' : 'input',                      #Use land mask from input file
        'land_file_name' : '/home/philbou/Isca/exp/test_cases/age_spectrum/frierson/continents/input/era_land_T42.nc',   #Tell model where to find input file
        'land_roughness_prefactor' : 10.0,            #How much rougher to make land than ocean
         'land_field_name' : 'land_mask',
         #'convection_scheme': 'NONE', # SIMPLE_BETTS_MILLER #Use the simple Betts Miller convection scheme from Frierson
        'convection_scheme': 'SIMPLE_BETTS_MILLER', # SIMPLE_BETTS_MILLER #Use the simple Betts Miller convection scheme from Frierson
    },

    'vert_turb_driver_nml': {
        'do_mellor_yamada': False,     # default: True
        'do_diffusivity': True,        # default: False
        'do_simple': True,             # default: False
        'constant_gust': 0.0,          # default: 1.0
        'use_tau': False
    },
    
    'diffusivity_nml': {
        'do_entrain':False,
        'do_simple': True,
    },

    'surface_flux_nml': {
        'use_virtual_temp': False,
        'do_simple': True,
        'old_dtaudv': True,
        'land_humidity_prefactor' : 1.0,
        'land_evap_prefactor' : 0.8,    
    },

    'atmosphere_nml': {
        'idealized_moist_model': True
    },

    #Use a large mixed-layer depth, and the Albedo of the CTRL case in Jucker & Gerber, 2017
    'mixed_layer_nml': {
        'tconst' : 285.,
        'prescribe_initial_dist':True,
        'evaporation':True,   
        'depth': 2.5,                          #Depth of mixed layer used
        'albedo_value': 0.31,                 #Albedo value used        
        'land_option' : 'input',              #Tell mixed layer to get land mask from input file
        'land_h_capacity_prefactor' : 0.1,    #What factor to multiply mixed-layer depth by over land. 
        'specify_sst_over_ocean_only' : True,  #Make sure sst only specified in regions of ocean. 
        'land_albedo_prefactor' : 1.3,        #What factor to multiply ocean albedo by over land    

    },

    'qe_moist_convection_nml': {
        'rhbm':0.7,
        'Tmin':160.,
        'Tmax':350.   
    },

    'betts_miller_nml': {
       'rhbm': .7   , 
       'do_simp': False, 
       'do_shallower': True, 
    },
    
    'lscale_cond_nml': {
        'do_simple':True,
        'do_evap':True
    },
    
    'sat_vapor_pres_nml': {
        'do_simple':True
    },
    
    'damping_driver_nml': {
        'do_rayleigh': True,
        'trayfric': -0.25,              # neg. value: time in *days*
        'sponge_pbottom':  5000.,           #Bottom of the model's sponge down to 50hPa (units are Pa)
        'do_conserve_energy': True,             
    },

    'two_stream_gray_rad_nml': {
        'rad_scheme': 'frierson',            #Select radiation scheme to use, which in this case is Frierson
        'do_seasonal': False,                #do_seasonal=false uses the p2 insolation profile from Frierson 2006. do_seasonal=True uses the GFDL astronomy module to calculate seasonally-varying insolation.
        'atm_abs': 0.2,                      # default: 0.0        
    },

    # FMS Framework configuration
    'diag_manager_nml': {
        'mix_snapshot_average_fields': False  # time avg fields are labelled with time in middle of window
    },

    'fms_nml': {
        'domains_stack_size': 600000                        # default: 0
    },

    'fms_io_nml': {
        'threading_write': 'single',                         # default: multi
        'fileset_write': 'single',                           # default: multi
    },

    'spectral_dynamics_nml': {
        'damping_order': 4,             
        'water_correction_limit': 200.e2,
        'reference_sea_level_press':1.0e5,
        'num_levels':25,               #How many model pressure levels to use
        'valid_range_t':[100.,800.],
        'initial_sphum':[2.e-6],
        'vert_coord_option':'input', #Use the vertical levels from Frierson 2006
        'surf_res':0.5,
        'scale_heights' : 11.0,
        'exponent':7.0,
        'robert_coeff':0.03
    },
    'vert_coordinate_nml': {
        'bk': [0.000000, 0.0117665, 0.0196679, 0.0315244, 0.0485411, 0.0719344, 0.1027829, 0.1418581, 0.1894648, 0.2453219, 0.3085103, 0.3775033, 0.4502789, 0.5244989, 0.5977253, 0.6676441, 0.7322627, 0.7900587, 0.8400683, 0.8819111, 0.9157609, 0.9422770, 0.9625127, 0.9778177, 0.9897489, 1.0000000],
        'pk': [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
       }
})

exp.set_resolution(*RESOLUTION)
#Lets do a run!
if __name__=="__main__":
    path  = os.getenv("GFDL_DATA")
    # Start from beginning
    res_file = '/home/philbou/scratch/isca_data/fr_T42_4mom_atdt/restarts/res0064.tar.gz'
    #exp.run(65, use_restart=True, restart_file=res_file, num_cores=NCORES,overwrite_data=True)
    exp.run(1, use_restart=False, num_cores=NCORES,overwrite_data=True)
    for i in range(2,241):
        exp.run(i ,num_cores=NCORES,overwrite_data=True)

