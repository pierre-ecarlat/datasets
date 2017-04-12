NB_IMAGES=$(cat dataset_9494.txt | wc -l)
NB_IMAGES_NS=$(cat dataset_9494.txt | grep "false;" | wc -l)

BOXES=$(cat dataset_9494.txt | grep "false;" | cut -d';' -f4 | cut -d'[' -f2 | cut -d']' -f1 | rev | cut -c 2- | rev | tr ":" "|")
IFS='\n'
readarray -t boxes <<<"$BOXES"

categs=""
for ((i=0; i<${#boxes[@]}; i++)); do 
  IFS='|' tmp=(${boxes[$i]})
  for ((j=0; j<${#tmp[@]}; j++)); do 
    IFS=' ' tmp2=(${tmp[$j]})
    categs+="${tmp2[0]} "
  done
  categs+="\n"
done 

echo -e $categs > output_categ.txt




categs=()
for ((i=0; i<67; i++)); do categs[$i]=0; done
readarray -t lines <<<"$(cat output_categ.txt)"
for ((i=0; i<${#lines[@]}; i++)); do 
  IFS=' ' tmp=(${lines[$i]})
  for ((j=0; j<${#tmp[@]}; j++)); do 
    tmp2=${tmp[$j]}
    ((categs[$tmp2]+=1))
  done
done 

categs_txt=""
for ((i=0; i<67; i++)); do categs_txt+="${categs[$i]}\n"; done

echo -e $categs_txt > output_categ_distrib.txt





boxes=()
readarray -t lines <<<"$(cat output_categ.txt)"
max=1
for ((i=0; i<${#lines[@]}; i++)); do 
  IFS=' ' tmp=(${lines[$i]})
  if [ $max -lt ${#tmp[@]} ]; then max=${#tmp[@]}; fi
done 
for ((i=0; i<$max; i++)); do boxes[$i]=0; done
for ((i=0; i<${#lines[@]}; i++)); do 
  IFS=' ' tmp=(${lines[$i]})
  ((boxes[${#tmp[@]}]+=1))
done 

boxes_distrib=""
for ((i=0; i<${#boxes[@]}; i++)); do boxes_distrib+="${boxes[$i]}\n"; done

echo -e $boxes_distrib > output_boxes_distrib.txt





NB_BOXES=0
readarray -t lines <<<"$(cat output_boxes_distrib.txt)"
for ((i=0; i<${#lines[@]}; i++)); do
  NB_BOXES=$((NB_BOXES + $i * lines[$i]))
done 

echo -e "nb_images: $NB_IMAGES\nnb_images_usable: $NB_IMAGES_NS\nnb_boxes: $NB_BOXES" > output_global.txt





awk '{printf("%01d %s\n", NR-1, $0)}' output_categ_distrib.txt | head -n -1 | sort -k2 -n > output_categ_distrib_idxes.txt
awk '{printf("%01d %s\n", NR-1, $0)}' dataset_9494.txt | grep "false;" | cut -d ' ' -f1 > tmp
paste tmp output_categ.txt | head -n -1 | tr "\t" " " > output_categ_idxes.txt
rm tmp
cp output_categ_idxes.txt output_categ_idxes_tmp.txt


trainval=()
test=()
readarray -t lines <<<"$(cat output_categ_distrib_idxes.txt)"
for ((l=0; l<${#lines[@]}; l++)); do
  IFS=' ' tmp=(${lines[$l]})
  curr_categ=${tmp[0]}
  
  list_imgs="$(cat output_categ_idxes_tmp.txt | grep \ $curr_categ\  | cut -d' ' -f1 | sort -R)"
  IFS='\n'
  readarray -t tmp2 <<<"$list_imgs"
  
  eighty=$((${#tmp2[@]} * 80 / 100))
  for ((i=0; i<$eighty; i++)); do
    trainval+=("${tmp2[$i]}")
  done
  for ((i=$eighty; i<${#tmp2[@]}; i++)); do
    test+=("${tmp2[$i]}")
  done
  
  awk '!/'\ $curr_categ\ '/' output_categ_idxes_tmp.txt > temp && mv temp output_categ_idxes_tmp.txt
done 

rm output_categ_idxes_tmp.txt

trainval_text=""
test_text=""
for ((i=0; i<${#trainval[@]}; i++)); do trainval_text+="${trainval[$i]};"; done
for ((i=0; i<${#test[@]}; i++)); do test_text+="${test[$i]};"; done

echo -e $trainval_text | tr ";" "\n" > trainval.txt
echo -e $test_text | tr ";" "\n" > test.txt




