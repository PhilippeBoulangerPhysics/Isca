#!/bin/bash

# === CONFIGURATION ===
FOLLOWUP_SCRIPTS=(
    "RT42_sst_0.py"
)
SBATCH_TEMPLATE_DIR="./sbatch_jobs"
mkdir -p "$SBATCH_TEMPLATE_DIR"

# === ENVIRONMENT SETUP BLOCK ===
read -r -d '' ENV_BLOCK << 'EOF'
export GFDL_BASE=/home/philbou/Isca
export GFDL_ENV=narval.ifort
export GFDL_WORK=/scratch/philbou/isca_work
export GFDL_DATA=/scratch/philbou/isca_data
source /home/philbou/.bashrc
conda activate isca_env
cd $GFDL_BASE/exp/test_cases/realistic_continents
EOF

# === GENERATE AND SUBMIT FOLLOW-UP JOBS ===
i=1
for script in "${FOLLOWUP_SCRIPTS[@]}"; do
    JOB_NAME="RT42_sst_4_$i"
    JOB_FILE="$SBATCH_TEMPLATE_DIR/job_$i.sbatch"

    cat <<EOF > "$JOB_FILE"
#!/bin/bash
#SBATCH --ntasks=32
#SBATCH --mem-per-cpu=3G
#SBATCH --time=0-12:00
#SBATCH --job-name=$JOB_NAME
#SBATCH --output=/scratch/philbou/outerr/%x-%j.out
#SBATCH --error=/scratch/philbou/outerr/%x-%j.err
#SBATCH --account=def-rfajber

$ENV_BLOCK

python $script
EOF

    sbatch "$JOB_FILE"
    echo "Submitted $JOB_FILE"
    ((i++))
done
