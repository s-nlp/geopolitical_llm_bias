# for lang in "fr" "he" "ru" "zh"; do
#     for model in "openai/gpt-oss-20b" "meta-llama/llama-4-maverick" "meta-llama/llama-4-scout" "qwen/qwen3-next-80b-a3b-thinking" "qwen/qwen3-30b-a3b-thinking-2507" "google/gemini-2.5-flash" "openai/gpt-5-mini" "deepseek/deepseek-v3.2-exp"; do
#         python3 evaluate.py \
#             --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
#             -l $lang \
#             --mode all \
#             --provider openai \
#             --base-url https://openrouter.ai/api/v1  \
#             --model $model  \
#             -k $OPENAI_API_KEY
#     done
# done

for lang in "fr" "he" "ru" "zh"; do
    for model in "openai/gpt-oss-20b" "meta-llama/llama-4-maverick" "qwen/qwen3-next-80b-a3b-thinking" "google/gemini-2.5-flash" "openai/gpt-5-mini" "deepseek/deepseek-v3.2-exp"; do
        python3 evaluate.py \
            --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
            -l $lang \
            --mode all \
            --provider openai \
            --base-url https://openrouter.ai/api/v1  \
            --model $model  \
            -k $OPENAI_API_KEY
    done
done

# "x-ai/grok-4-fast" "x-ai/grok-4" "x-ai/grok-3-mini" # NEED VPN

# for model in "nousresearch/hermes-4-70b" "nousresearch/hermes-4-405b" "z-ai/glm-4.6" "z-ai/glm-4.5" "z-ai/glm-4.5-air" "openai/gpt-5-nano" "openai/gpt-oss-120b" "google/gemini-2.5-pro" "anthropic/claude-sonnet-4.5" "anthropic/claude-3.5-haiku" "moonshotai/kimi-k2-0905" "mistralai/mistral-medium-3.1" "deepseek/deepseek-v3.1-terminus" "bytedance/seed-oss-36b-instruct"; do
#     python3 evaluate.py \
#         --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
#         -l en \
#         --mode all \
#         --provider openai \
#         --base-url https://openrouter.ai/api/v1  \
#         --model $model  \
#         -k $OPENAI_API_KEY
# done

# for lang in "ar" "fr" "he" "ru" "zh"; do
#     python3 evaluate.py \
#         --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
#         -l $lang \
#         --mode all \
#         --provider openai \
#         --base-url https://foundation-models.api.cloud.ru/v1  \
#         --model "GigaChat/GigaChat-2-Max"  \
#         -k "MDlhNGM0YjQtZmEzZi00NzAyLTlhYTEtMDE2NGNjOWY3OTZh.be6efd73a83c43af23de5163dcdd1ad7"
# done


# for model in "openai/gpt-oss-20b" "meta-llama/llama-4-maverick" "meta-llama/llama-4-scout" "qwen/qwen3-next-80b-a3b-thinking" "qwen/qwen3-30b-a3b-thinking-2507" "google/gemini-2.5-flash" "openai/gpt-5-mini" "deepseek/deepseek-v3.2-exp"; do
#     python3 evaluate.py \
#         --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
#         -l en \
#         --mode all \
#         --provider openai \
#         --base-url https://openrouter.ai/api/v1  \
#         --model $model  \
#         -k $OPENAI_API_KEY \
#         --chinese-patriot
# done




# for model in "openai/gpt-oss-20b"; do #"meta-llama/llama-4-maverick" "meta-llama/llama-4-scout" "qwen/qwen3-next-80b-a3b-thinking" "qwen/qwen3-30b-a3b-thinking-2507" "google/gemini-2.5-flash" "openai/gpt-5-mini" "deepseek/deepseek-v3.2-exp"; do
#     python3 evaluate.py \
#         --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
#         -l en \
#         --mode all \
#         --provider openai \
#         --base-url https://openrouter.ai/api/v1  \
#         --model $model  \
#         -k $OPENAI_API_KEY \
#         --chinese-patriot
# done



# python3 evaluate.py \
#     --data-file ./data_mining/data2/final_dataset_propaganda_cleaned_translated.json \
#     -l en \
#     --mode all \
#     --provider openai \
#     --base-url http://localhost:8000/v1  \
#     --model openai/gpt-oss-20b  \
#     -k None \
#     --chinese-patriot