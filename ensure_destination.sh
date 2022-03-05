DESTINATION=''

while getopts 'd:' flag; do
  case "${flag}" in
    d) DESTINATION="$OPTARG";;
    *) ;;
  esac
done

# Guard clause, destination folder must exist
if ! [ -d "$DESTINATION" ]
then
  echo "destination folder '${DESTINATION}' not found!"
  mkdir $DESTINATION || \
    { echo "ERROR: could not create destination folder! exiting ..."; exit 1; }
  echo "created destination folder '${DESTINATION}'"
fi