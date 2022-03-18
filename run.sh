DESTINATION=src/generated

if [ "$#" != 1 ];
 then
    exit 1;
fi

chmod +x ensure_destination.sh
./ensure_destination.sh -d $DESTINATION

FILE_COUNT=$(find $DESTINATION -name "*Parser.py" | wc -l)
if [ $FILE_COUNT -ne 1 ]
then
  echo "ANTLR generated files not found"
  chmod +x generate.sh
  ./generate.sh
fi

FILE_COUNT=$(find $DESTINATION -name  "*Parser.py" | wc -l)
if [ $FILE_COUNT -eq 1 ]
then
  echo "calling main.py"
  python3 main.py $1
  exit 0
fi

echo "ERROR: could not find ANTLR generated files"
exit 1
