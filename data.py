"""
Deterministic in-memory dataset of 200 books.
Each book has 20 fields to simulate REST over-fetching.
"""

import random

ADJECTIVES = [
    "Lost", "Hidden", "Golden", "Silent", "Dark", "Eternal", "Forgotten", "Ancient",
    "Broken", "Sacred", "Wild", "Distant", "Shattered", "Crimson", "Midnight",
    "Ivory", "Hollow", "Burning", "Frozen", "Whispered", "Shining", "Bitter",
    "Stormy", "Graceful", "Luminous",
]

NOUNS = [
    "Kingdom", "Symphony", "Labyrinth", "Garden", "Storm", "Promise", "Echo", "Shadow",
    "Mirror", "River", "Mountain", "Legend", "Secret", "Journey", "Throne",
    "Ocean", "Forest", "Dream", "Ghost", "Phoenix", "Compass", "Chronicle",
    "Horizon", "Silence", "Covenant",
]

AUTHOR_NAMES = [
    "Gabriel Silva", "Maria Santos", "João Oliveira", "Ana Costa", "Pedro Souza",
    "Emma Johnson", "James Williams", "Sarah Brown", "Michael Davis", "Emily Wilson",
    "Chen Wei", "Yuki Tanaka", "Pierre Dubois", "Sophie Laurent", "Hans Mueller",
    "Isabella Romano", "Carlos Mendez", "Fatima Al-Hassan", "Raj Patel", "Amara Obi",
]

AUTHOR_BIOS = [
    "A prolific writer born in São Paulo and celebrated across Latin America, known for groundbreaking contributions to contemporary Brazilian literature. Their work has been translated into over thirty languages and has received the Casa de las Américas Prize, among other notable distinctions in the literary world.",
    "An internationally acclaimed thriller author whose psychological novels have dominated bestseller lists for over a decade. A graduate of Oxford University with a background in forensic psychology, they divide their time between London and New York City.",
    "Raised in rural Japan, this celebrated poet and novelist draws deeply from nature and Zen philosophy. Their minimalist prose style has influenced a generation of writers, and their debut novel won the Akutagawa Prize and was adapted into an award-winning film.",
    "A former war correspondent turned novelist, this author brings firsthand experience of conflict zones to their fiction. Their books blend geopolitical intrigue with intimate human drama, and they have been shortlisted for the Booker Prize three times.",
    "A mathematician and fiction writer whose novels explore the intersection of science and the human experience. Educated at MIT and the Sorbonne, they have been praised for making complex ideas accessible without sacrificing intellectual depth.",
    "Born in Lagos and educated in London, this author writes about the African diaspora experience with unflinching honesty and poetic grace. Their debut collection of short stories won the Caine Prize and launched one of the most talked-about literary careers of their generation.",
    "A celebrated historian and bestselling author specializing in medieval Europe, with multiple New York Times bestsellers to their name. Their narrative non-fiction approach has brought often-overlooked historical periods to life for millions of readers worldwide.",
    "A celebrated children's and young adult author whose fantasy novel series has sold over fifty million copies globally. Their world-building and inclusive storytelling have garnered both critical acclaim and devoted fanbases in more than forty countries.",
    "An Argentine author working in the tradition of magical realism, often compared to García Márquez and Borges. Their dense, allusive prose rewards patient readers and their third novel has been included in several lists of the best Latin American novels of the century.",
    "A Canadian author and environmental activist whose novels dramatize the consequences of ecological collapse. Their work sits at the intersection of speculative fiction and documentary realism, earning them a reputation as one of the most urgent voices in contemporary literature.",
    "Trained as a physician and practicing medicine for fifteen years before turning to writing full time, this author brings clinical precision and deep human empathy to stories of illness, mortality, and healing. Their memoir was awarded the National Book Award.",
    "A queer South Korean author whose experimental novels have pushed the boundaries of Korean literary fiction. They have been the subject of major international retrospectives and are widely regarded as one of the most significant literary voices of their generation.",
    "An Italian crime novelist whose detective series set in Venice has been adapted into a long-running television drama. Known for their atmospheric prose and intricate plotting, they have won the Gold Dagger from the Crime Writers' Association.",
    "A philosopher and essayist who turned to fiction later in life, writing dense intellectual novels that grapple with questions of free will, consciousness, and political power. Their work has been translated into twenty languages and they hold honorary degrees from four universities.",
    "Born in Mumbai and raised partly in the United States, this author writes about the Indian-American experience with humor, warmth, and sharp social observation. Their debut novel was longlisted for the Dublin Literary Award and praised for its vivid characterization.",
    "A Puerto Rican author who writes across genres including literary fiction, horror, and science fiction, often blending them in unexpected ways. They teach creative writing at a major research university and are known for their mentorship of emerging Latinx writers.",
    "A French-Algerian author whose novels explore colonialism, memory, and belonging with lyrical intensity. Their work has provoked significant literary and political debate in France, and they are a frequent guest at major international literature festivals.",
    "A former Silicon Valley engineer turned literary novelist, whose satirical novels about technology culture have won praise for their prescience and wit. They are also a popular speaker on the social impact of artificial intelligence and digital surveillance.",
    "A debut novelist who emerged from an MFA program to immediate critical acclaim. Their first novel, which explores generational trauma in a small coastal town, was selected for numerous prestigious book clubs and won multiple awards for debut fiction.",
    "An elderly South African author who has been writing quietly for fifty years, gaining widespread international recognition only recently. Their collected works offer a sweeping portrait of South Africa from apartheid to the present day.",
]

AUTHOR_NATIONALITIES = [
    "Brazilian", "Brazilian", "Brazilian", "Brazilian", "Brazilian",
    "British", "American", "American", "American", "American",
    "Chinese", "Japanese", "French", "French", "German",
    "Italian", "Mexican", "Egyptian", "Indian", "Nigerian",
]

GENRES = [
    "Literary Fiction", "Thriller", "Science Fiction", "Mystery", "Biography",
    "History", "Romance", "Fantasy", "Self-help", "Non-fiction",
]

DESCRIPTIONS = [
    "In this deeply moving debut, the author explores the aftermath of a family tragedy through the perspectives of three siblings who have spent decades avoiding each other. Set against the backdrop of a dying industrial town in the Midwest, the novel examines how grief, guilt, and silence can fracture even the most resilient of families. With luminous prose and unflinching emotional honesty, it asks whether the bonds of blood are ever truly broken, even when they have been stretched beyond all recognition by years of absence and misunderstanding.",
    "A thrilling journey into the heart of a conspiracy that reaches the highest levels of government and finance. When a forensic accountant discovers an anomaly in the books of one of the world's most powerful hedge funds, she is drawn into a deadly game of pursuit and deception that spans four continents. Fast-paced and meticulously researched, this novel keeps the reader guessing until the final shocking revelation on the very last page of this gripping international thriller.",
    "Set a century from now on a terraformed Mars, this sweeping science fiction epic follows the last generation of colonists as they grapple with the decision to sever ties with an Earth that is rapidly becoming uninhabitable. Blending hard science with profound meditations on identity, belonging, and the nature of home, the novel is a landmark of contemporary speculative fiction and an urgent warning about the paths humanity may be forced to take in the coming decades.",
    "A fiercely intelligent detective novel set in the crumbling grandeur of 1930s Havana. When the body of a prominent sugar baron is found floating in the harbor, Inspector Alejandro Cruz must navigate a world of corrupt officials, desperate exiles, and revolutionary idealists to uncover the truth. Rich in historical detail and morally ambiguous characters, this mystery is as much a portrait of a society on the brink of transformation as it is a classic whodunit.",
    "A landmark biography of one of the twentieth century's most controversial and influential figures, drawing on decades of archival research and over two hundred previously unpublished letters. The author does not seek to rehabilitate or condemn, but to understand, presenting a nuanced portrait of a person whose public legacy has long overshadowed the complex human being behind it. Essential reading for anyone interested in modern political and cultural history.",
    "A gripping popular history of the construction of the Panama Canal, told through the lives of the workers, engineers, politicians, and dreamers who made it possible—and the tens of thousands who died in the attempt. Drawing on sources in four languages, the author brings the epic scale of the project down to a profoundly human level, revealing the ambition, hubris, and extraordinary courage that shaped one of the modern world's greatest engineering achievements.",
    "A sweeping multi-generational romance that spans four decades and three continents, following two families whose destinies are intertwined by a chance encounter during the summer of 1968 in Paris. Told in alternating voices and timelines, the novel is a celebration of love's endurance in the face of war, political upheaval, and the ordinary erosions of time. Emotionally rich and beautifully written, it confirms its author as one of the great storytellers of their generation.",
    "The long-awaited third installment in an epic fantasy series, in which the exiled queen must forge an unlikely alliance with her greatest enemy to prevent the opening of a gateway to a realm of pure chaos. Building on the intricately constructed world of its predecessors, this volume deepens the mythology and raises the moral stakes, delivering battle sequences of stunning choreography alongside moments of quiet, devastating emotional power that will stay with readers long after the last page.",
    "A practical and compassionate guide to reclaiming focus and mental clarity in an age of constant distraction. Drawing on the latest research from neuroscience, psychology, and productivity studies, the author provides a step-by-step programme for restructuring daily life around what truly matters. Accessible, evidence-based, and full of actionable strategies, this book has already helped thousands of readers transform their relationship with time and attention.",
    "A brilliant and surprising work of narrative non-fiction that reconstructs a single extraordinary day in the life of a mid-sized American city during the summer of 1943, drawing on contemporary diaries, newspaper accounts, FBI files, and oral history interviews. A masterclass in the possibilities of the form and a deeply moving tribute to ordinary lives lived in extraordinary times during one of the most turbulent periods of the twentieth century.",
]

PUBLISHERS = [
    "Penguin Random House", "HarperCollins", "Simon & Schuster",
    "Hachette Book Group", "Macmillan Publishers", "Oxford University Press",
    "Cambridge University Press", "Bloomsbury Publishing", "Knopf Doubleday", "Farrar, Straus and Giroux",
]

LANGUAGES = ["English", "Portuguese", "Spanish", "French", "German", "Italian", "Japanese"]

SERIES_NAMES = [
    "The Chronicles of Aeloria", "The Meridian Saga", "The Hollow Earth Sequence",
    "The Compass Rose Trilogy", "The Age of Silence", "The Red Meridian",
    "The Cartographer's Legacy", "The Dark Water Series", "The Amber Archives", "The Iron Covenant",
]

KEYWORDS_POOL = [
    "identity", "family", "loss", "redemption", "history", "power", "love",
    "betrayal", "survival", "justice", "memory", "war", "freedom", "science",
    "nature", "politics", "religion", "art", "music", "technology", "race",
    "class", "gender", "diaspora", "belonging", "grief", "hope", "trauma", "healing",
]

ALL_AWARDS = [
    "Pulitzer Prize", "National Book Award", "Man Booker Prize", "Hugo Award",
    "Edgar Allan Poe Award", "Nebula Award", "Caine Prize", "Akutagawa Prize",
]


def generate_books(n: int = 200, seed: int = 42) -> list:
    rng = random.Random(seed)
    books = []
    for i in range(1, n + 1):
        author_idx = (i - 1) % len(AUTHOR_NAMES)
        has_series = (i % 4 == 0)
        series_idx = ((i // 4) - 1) % len(SERIES_NAMES) if has_series else None
        num_awards = rng.randint(0, 2)
        awards = rng.sample(ALL_AWARDS, num_awards)
        kw_start = (i - 1) % len(KEYWORDS_POOL)
        keywords = [KEYWORDS_POOL[(kw_start + j) % len(KEYWORDS_POOL)] for j in range(5)]

        books.append({
            "id": i,
            "title": f"The {ADJECTIVES[(i - 1) % len(ADJECTIVES)]} {NOUNS[(i - 1) % len(NOUNS)]}",
            "author_name": AUTHOR_NAMES[author_idx],
            "author_bio": AUTHOR_BIOS[author_idx],
            "author_nationality": AUTHOR_NATIONALITIES[author_idx],
            "year_published": 1970 + (i * 7 % 54),
            "genre": GENRES[(i - 1) % len(GENRES)],
            "description": DESCRIPTIONS[(i - 1) % len(DESCRIPTIONS)],
            "rating": round(3.0 + (i * 0.01 % 2.0), 2),
            "pages": 150 + (i * 37 % 750),
            "publisher": PUBLISHERS[(i - 1) % len(PUBLISHERS)],
            "isbn": f"978-{str(1000000000 + (i * 123456789) % 9000000000).zfill(10)}",
            "language": LANGUAGES[(i - 1) % len(LANGUAGES)],
            "series_name": SERIES_NAMES[series_idx] if has_series else None,
            "series_number": (i % 5 + 1) if has_series else None,
            "awards": awards,
            "keywords": keywords,
            "cover_url": f"https://covers.openlibrary.org/b/id/{10000 + i}-L.jpg",
            "price": round(9.99 + (i * 1.23 % 40.00), 2),
            "stock_count": i * 7 % 500,
        })
    return books


if __name__ == "__main__":
    import json
    books = generate_books()
    sample = books[0]
    size = len(json.dumps(sample).encode("utf-8"))
    print(f"Generated {len(books)} books.")
    print(f"Fields per book: {len(sample)}")
    print(f"Single book JSON size: {size} bytes")
    print(f"Sample: {json.dumps(sample, indent=2, ensure_ascii=False)[:500]}...")
