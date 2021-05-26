#$1 <track> : "1","2" or "3"
#$2 <subset> : "train", "dev", "test"

python3 src/NORM/pre_process_norm.py "single_ont" $1 $2

cd src/NORM

java ppr_for_ned_all "single_ont"

cd ../../

python3 src/NORM/post_process_norm.py "single_ont" $1 $2
