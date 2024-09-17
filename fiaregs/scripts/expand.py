import pandas as pd

exp_id = 9

responses = {}
for i in range(3):
    df = pd.read_csv(f'exp_{exp_id}/eval_{i+1}.csv')
    for _,row in df.iterrows():
        q = row['question']
        answers = responses.get(q, None)
        if answers is None:
            answers = {
                'ground_truth': row['ground_truth'],
                'answers': [row['answer']],
                'eval': [row['binary_answer_correctness']]
            }
        else:
            answers['answers'].append(row['answer'])
            answers['eval'].append(row['binary_answer_correctness'])

        responses[q] = answers

for q,a in responses.items():
    print(f'Question: {q}')
    print(f'Truth: {a["ground_truth"]}')
    print()
    for ev,ans in zip(a['eval'], a['answers']):
        print(f'Answer: {ans}')
        print(f'Eval score: {ev}')
        print()
    print('-'*45)
    print()