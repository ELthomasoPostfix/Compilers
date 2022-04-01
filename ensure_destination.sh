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
    -h :  Show this help message
    -d :  Specify a destination directory, the default is '${DESTINATION_DIR}'
    -o :  Specify an output directory, the default is '${OUTPUT_DIR}'"
  exit 0
fi

# Guard clause, destination directory must exist
if ! [ -d "$DESTINATION_DIR" ]
then
  echo "Destination directory '${DESTINATION_DIR}' not found!"
  mkdir $DESTINATION_DIR || \
    { echo "ERROR: could not create destination directory! exiting ..."; exit 1; }
  echo "Created destination directory"
fi

# Guard clause, output directory must exist
if ! [ -d "$OUTPUT_DIR" ]
then
  echo "Output directory '${OUTPUT_DIR}' not found!"
  mkdir $OUTPUT_DIR || \
    { echo "ERROR: could not create output directory! exiting ..."; exit 1; }
  echo "Created output directory"
fi