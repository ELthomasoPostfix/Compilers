GRAMMAR_LOC=Input
DESTINATION=../src/generated
cd $GRAMMAR_LOC || { echo "ERROR: Could not find grammar location, $GRAMMAR_LOC"; exit 1; }
java -jar antlr-4.9.3-complete.jar -o $DESTINATION -Dlanguage=Python3 MyGrammar.g4 -visitor
