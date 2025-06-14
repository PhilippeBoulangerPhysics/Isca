#!/bin/bash
#SBATCH --ntasks=32
#SBATCH --mem-per-cpu=3G
#SBATCH --time=0-12:00
#SBATCH --job-name=real_T85_plev_spin_def
#SBATCH --output=/scratch/philbou/outerr/%x-%j.out
#SBATCH --error=/scratch/philbou/outerr/%x-%j.err
#SBATCH --account=def-rfajber

#not sure if this is needed but just in case 
# directory of the Isca source code
export GFDL_BASE=/home/philbou/Isca 
# &quot;environment&quot; configuration for emps-gv4
export GFDL_ENV=narval.ifort
# temporary working directory used in running the model
export GFDL_WORK=/scratch/philbou/isca_work
# directory for storing model output
export GFDL_DATA=/scratch/philbou/isca_data

#conda init bash
#conda activate isca_env

source /home/philbou/.bashrc 
conda activate isca_env

cd $GFDL_BASE/exp/test_cases/realistic_continents

python real_cont_fixed_sst_climrun.py
