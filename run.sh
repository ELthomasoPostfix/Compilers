FILE_COUNT=$(find src/generated -name "*Parser.py" | wc -l)
if [ $FILE_COUNT -ne 1 ]
then
  echo "ANTLR generated files not found"
  echo "calling ANTLR ..."
  sudo chmod +x generate.sh
  ./generate.sh
  echo "finished calling ANTLR"
fi

FILE_COUNT=$(find src/generated -name  "*Parser.py" | wc -l)
if [ $FILE_COUNT -eq 1 ]
then
  echo "calling main.py"
  python3 src/main.py
  exit 0
fi

echo "ERROR: could not find ANTLR generated files"
exit 1
