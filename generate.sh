c_flag=false  # Clean destination folder before generation
h_flag=false  # Display help
GRAMMAR_LOC=Input
DESTINATION=src/generated

# Guard clause, destination folder must exist
if ! [ -d "$DESTINATION" ]
then
  echo "ERROR: destination folder '${DESTINATION}' not found"
  exit 1;
fi

while getopts 'ch' flag; do
  case "${flag}" in
    c) c_flag=true ;;
    h) h_flag=true ;;
    *) echo "unknown flag ${flag}";;
  esac
done

# Do cleanup flag
if [ "$h_flag" = true ]
then
  echo "Call ANTLR using 'java -jar' in the subdirectory '${GRAMMAR_LOC}' to generate python files based on the grammar located in subdirectory ${GRAMMAR_LOC} into destination subdirectory '${DESTINATION}'.
   possible flags:
    -h :  display help and exit without calling ANTLR
    -c :  remove all files in the destination folder before calling ANTLR"
  exit 0
elif [ "$c_flag" = true ]
then
  rm src/generated/*
fi
cd $GRAMMAR_LOC || { echo "ERROR: Could not find grammar location, $GRAMMAR_LOC"; exit 1; }
java -jar antlr-4.9.3-complete.jar -o ../$DESTINATION -Dlanguage=Python3 MyGrammar.g4 -visitor
