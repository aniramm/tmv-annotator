#!/usr/bin/sh


# User parameters
while getopts i:l:h: option
do
        case "${option}"
        in
                i) INPUT=${OPTARG};;
                l) LANG=${OPTARG};;
                h) HTML=${OPTARG};;
        esac
done

OUTPUT=$(basename $INPUT) # Output file name
TMV_SCRIPTS=$(pwd) # Path to annotation scripts
mkdir -p $TMV_SCRIPTS/output # Directory for output files

if [ "$LANG" = "de" ]; then

    python $TMV_SCRIPTS/TMV-DE.py $INPUT $OUTPUT $TMV_SCRIPTS/seinVerbs.txt
    if [ "$HTML" = "yes" ]; then
	python TMVtoHTML.py output/$OUTPUT.verbs $INPUT $LANG
    fi
    
elif [ "$LANG" = "en" ]; then

    python $TMV_SCRIPTS/TMV-EN.py $INPUT $OUTPUT
    if [ "$HTML" = "yes" ]; then
	python TMVtoHTML.py output/$OUTPUT.verbs $INPUT $LANG
    fi

elif [ "$LANG" = "fr" ]; then

    python $TMV_SCRIPTS/TMV-FR.py $INPUT $OUTPUT
    if [ "$HTML" = "yes" ]; then
	python TMVtoHTML.py output/$OUTPUT.verbs  $INPUT $LANG
    fi

else
    echo "Unknown language!"
    exit
    
    fi


