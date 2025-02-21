from dotenv import load_dotenv
from phoenix.trace import SpanEvaluations

load_dotenv('../envs/deepseek.env')

import os

from phoenix import Client

phoenix_client = Client()

# Get all the spans
df = phoenix_client.get_spans_dataframe(project_name=os.environ['ARIZE_PROJECT_NAME'])
eval_df_all = df[['context.span_id', 'attributes.llm.output_messages']].copy()
eval_df = eval_df_all[eval_df_all['attributes.llm.output_messages'].notna()]  # filter spans with a valid output

# Run evaluations
eval_df['score'] = eval_df['attributes.llm.output_messages'].apply(lambda x: len(x[0].get('message.content')))
eval_df['label'] = eval_df['score'].apply(lambda s: 'low' if s <= 500 else ('medium' if s < 1500 else 'high'))
eval_df['score'] = eval_df['score'].astype(int)
print(eval_df.head()[['score', 'label']])

# Store the evaluations
phoenix_client.log_evaluations(SpanEvaluations(eval_name="Character Count", dataframe=eval_df))
