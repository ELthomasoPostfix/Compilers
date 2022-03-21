c_flag=false  # Clean destination folder before generation
h_flag=false  # Display help
GRAMMAR_LOC=Input
DESTINATION=src/generated

chmod +x ensure_destination.sh
./ensure_destination.sh -d $DESTINATION

while getopts 'ch' flag; do
  case "${flag}" in
    c) c_flag=true ;;
    h) h_flag=true ;;
    *) ;;
  esac
done

# Display help
if [ "$h_flag" = true ]
then
  echo "Call ANTLR using 'java -jar' in the subdirectory '${GRAMMAR_LOC}' to generate python files based on the grammar located in subdirectory ${GRAMMAR_LOC} into destination subdirectory '${DESTINATION}'. Will attempt to create the destination folder if it does not exist.
   possible flags:
    -h :  Show this help message
    -c :  remove all files in the destination folder before calling ANTLR"
  exit 0
# Do pre-generation cleanup
elif [ "$c_flag" = true ]
then
  rm src/generated/*
fi
cd $GRAMMAR_LOC || { echo "ERROR: Could not find grammar location, $GRAMMAR_LOC"; exit 1; }
echo "calling ANTLR ..."
java -jar antlr-4.9.3-complete.jar -o ../$DESTINATION -Dlanguage=Python3 MyGrammar.g4 -visitor
echo "finished calling ANTLR"
