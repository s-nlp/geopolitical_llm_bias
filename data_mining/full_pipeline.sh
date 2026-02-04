for pair in "(USA,USSR)" "(USA,UK)" "(USA,China)" "(UK,China)" "(China,USSR)" "(USSR,UK)"; do
    country1=$(echo $pair | sed 's/(\([^,]*\),\([^)]*\))/\1/')
    country2=$(echo $pair | sed 's/(\([^,]*\),\([^)]*\))/\2/')
    echo "Processing pair: \"$country1\", \"$country2\""

    #python3 discover.py $country1 $country2 --discover-output ./data/${country1}_${country2}_discovered.json --max-events 200
    python3 cluster_unique.py --input ./data/${country1}_${country2}_discovered.json --output ./data/${country1}_${country2}_discovered_unique.json
    # python3 finalize_processing.py --input ./data/${country1}_${country2}_discovered_unique.json --output ./data/${country1}_${country2}_final.json
done
