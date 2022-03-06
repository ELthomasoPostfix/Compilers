h_flag=false
DESTINATION_DIR=src/generated
OUTPUT_DIR=Output

while getopts 'hd:o:' flag; do
  case "${flag}" in
    h) h_flag=true ;;
    d) DESTINATION_DIR="$OPTARG" ;;
    o) OUTPUT_DIR="$OPTARG" ;;
    *) ;;
  esac
done

# Display help
if [ "$h_flag" = true ]
then
  echo "Ensures the directories needed by the compiler exist.
   possible flags:
    -h :  display help and exit without ensuring directory existence
    -d :  specify a destination directory, the default is '${DESTINATION_DIR}'
    -o :  specify an output directory, the default is '${OUTPUT_DIR}'"
  exit 0
fi

# Guard clause, destination directory must exist
if ! [ -d "$DESTINATION_DIR" ]
then
  echo "destination directory '${DESTINATION_DIR}' not found!"
  mkdir $DESTINATION_DIR || \
    { echo "ERROR: could not create destination directory! exiting ..."; exit 1; }
  echo "created destination directory"
fi

# Guard clause, output directory must exist
if ! [ -d "$OUTPUT_DIR" ]
then
  echo "output directory '${OUTPUT_DIR}' not found!"
  mkdir $OUTPUT_DIR || \
    { echo "ERROR: could not create output directory! exiting ..."; exit 1; }
  echo "created output directory"
fi