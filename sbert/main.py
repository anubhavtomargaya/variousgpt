from sentence_transformers import SentenceTransformer,util, InputExample, losses
from torch.utils.data import DataLoader



def embed():
    model = SentenceTransformer('all-MiniLM-L6-v2')

    #Our sentences we like to encode
    sentences = ['This framework generates embeddings for each input sentence',
        'Sentences are passed as a list of string.', 
        'The quick brown fox jumps over the lazy dog.']

    #Sentences are encoded by calling model.encode()
    sentence_embeddings = model.encode(sentences)

    #Print the embeddings
    for sentence, embedding in zip(sentences, sentence_embeddings):
        print("Sentence:", sentence)
        print("Embedding:", embedding)

        print("")


def cossim():
    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    #Sentences are encoded by calling model.encode()
    emb1 = model.encode("This is a red cat with a hat.")
    emb2 = model.encode("Have you seen my red cat?")

    cos_sim = util.cos_sim(emb1, emb2)
    print("Cosine-Similarity:", cos_sim)


def cossimarray():
    model = SentenceTransformer('all-MiniLM-L6-v2')

    sentences = ['A man is eating food.',
            'A man is eating a piece of bread.',
            'The girl is carrying a baby.',
            'A man is riding a horse.',
            'A woman is playing violin.',
            'Two men pushed carts through the woods.',
            'A man is riding a white horse on an enclosed ground.',
            'A monkey is playing drums.',
            'Someone in a gorilla costume is playing a set of drums.'
            ]

    #Encode all sentences
    embeddings = model.encode(sentences)

    #Compute cosine similarity between all pairs
    cos_sim = util.cos_sim(embeddings, embeddings)

    #Add all pairs to a list with their cosine similarity score
    all_sentence_combinations = []
    for i in range(len(cos_sim)-1):
        for j in range(i+1, len(cos_sim)):
            all_sentence_combinations.append([cos_sim[i][j], i, j])

    #Sort list by the highest cosine similarity score
    all_sentence_combinations = sorted(all_sentence_combinations, key=lambda x: x[0], reverse=True)

    print("Top-5 most similar pairs:")
    for score, i, j in all_sentence_combinations[0:5]:
        print("{} \t {} \t {:.4f}".format(sentences[i], sentences[j], cos_sim[i][j]))


def semanticsearch():
    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

    query_embedding = model.encode('How big is London')
    passage_embedding = model.encode(['London has 9,787,426 inhabitants at the 2011 census',
                                    'London is known for its finacial district'])

    print("Similarity:", util.dot_score(query_embedding, passage_embedding))

def trainmodel():

    #Define the model. Either from scratch of by loading a pre-trained model
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')

    #Define your train examples. You need more than just two examples...
    train_examples = [InputExample(texts=['My first sentence', 'My second sentence'], label=0.8),
        InputExample(texts=['Another pair', 'Unrelated sentence'], label=0.3)]

    #Define your train dataset, the dataloader and the train loss
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    train_loss = losses.CosineSimilarityLoss(model)

    #Tune the model
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=100)


semanticsearch()