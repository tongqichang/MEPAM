
for file in ./MEPAM_NER/data/100txt/*.txt; do
  output_file="/NER/data/qwen/$(basename "$file" .txt).yaml"
  ontogpt -v extract -t ./MEPAM_NER/scripts/enzyme_noid3.yaml -i "$file"  --model openai/gpt-4o --api-base=https://xiaoai.plus/v1 --temperature 0 > -O yaml -o "$output_file" --temperature 0  -O json -o "$output_file"
  #sleep 10
  
done
