"""
Enhanced Seed Script for Retrieval Audit
Generates 50 resources across 5 distinct semantic clusters
"""
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource, Annotation, Base

# Import embedding logic
try:
    from sentence_transformers import SentenceTransformer
    from FlagEmbedding import BGEM3FlagModel
except ImportError:
    print("CRITICAL: ml-dependencies not found. Run 'pip install sentence-transformers FlagEmbedding'")
    sys.exit(1)

DB_URL = "sqlite:///./backend.db"

# --- CONFIGURATION ---
CLUSTERS = {
    "CODING": [
        ("Python Asyncio", "Asyncio is a library to write concurrent code using the async/await syntax. Essential for I/O bound tasks."),
        ("Postgres Indexing", "B-Tree is the default index type in PostgreSQL. It fits most common scenarios."),
        ("React Hooks", "Hooks let you use state and other React features without writing a class component."),
        ("Docker Containers", "A container is a standard unit of software that packages up code and all its dependencies."),
        ("Kubernetes Pods", "Pods are the smallest deployable units of computing that you can create and manage in Kubernetes."),
        ("REST API Design", "REST is an architectural style that defines a set of constraints to be used for creating web services."),
        ("GraphQL vs REST", "GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data."),
        ("Git Branching", "Branching means you diverge from the main line of development and continue to do work without messing with that main line."),
        ("CI/CD Pipelines", "Continuous Integration and Continuous Delivery are methods to frequently deliver apps to customers by introducing automation."),
        ("SOLID Principles", "SOLID is a mnemonic acronym for five design principles intended to make software designs more understandable, flexible, and maintainable.")
    ],
    "COOKING": [
        ("Sourdough Starter", "A sourdough starter is a culture of wild yeast and lactobacilli used to leaven bread."),
        ("Carbonara Authentic", "Authentic Carbonara uses guanciale, pecorino romano, eggs, and black pepper. No cream."),
        ("Maillard Reaction", "The Maillard reaction is a chemical reaction between amino acids and reducing sugars that gives browned food its distinctive flavor."),
        ("Sous Vide", "Sous vide is a method of cooking in which food is placed in a plastic pouch or a glass jar and cooked in a water bath."),
        ("Knife Skills", "The claw grip is essential for safe chopping. Keep your fingertips curled under your knuckles."),
        ("Mother Sauces", "The five French mother sauces are Béchamel, Velouté, Espagnole, Hollandaise, and Tomato."),
        ("Wok Hei", "Wok hei is the complex charred flavor and aroma that results from stir-frying over very high heat."),
        ("Tempering Chocolate", "Tempering is the process of heating and cooling chocolate to specific temperatures to stabilize the cocoa butter crystals."),
        ("Umami Flavor", "Umami is one of the five basic tastes. It has been described as savory and is characteristic of broths and cooked meats."),
        ("Fermentation", "Fermentation is a metabolic process that produces chemical changes in organic substrates through the action of enzymes.")
    ],
    "HISTORY": [
        ("Fall of Rome", "The Fall of the Western Roman Empire was the process of decline in the Western Roman Empire."),
        ("Industrial Revolution", "The Industrial Revolution was the transition to new manufacturing processes in Great Britain, continental Europe, and the United States."),
        ("Magna Carta", "Magna Carta Libertatum is a royal charter of rights agreed to by King John of England at Runnymede."),
        ("The Cold War", "The Cold War was a period of geopolitical tension between the United States and the Soviet Union."),
        ("Renaissance Art", "The Renaissance was a fervent period of European cultural, artistic, political and economic 'rebirth' following the Middle Ages."),
        ("Silk Road", "The Silk Road was a network of trade routes connecting the East and West."),
        ("French Revolution", "The French Revolution was a period of radical political and societal change in France."),
        ("Maya Civilization", "The Maya civilization was a Mesoamerican civilization developed by the Maya peoples."),
        ("World War I", "World War I was a global conflict that originated in Europe and lasted from 28 July 1914 to 11 November 1918."),
        ("The Moon Landing", "Apollo 11 was the American spaceflight that first landed humans on the Moon.")
    ],
    "LEGAL": [
        ("Tort Law", "A tort is a civil wrong that causes a claimant to suffer loss or harm, resulting in legal liability for the person who commits the tort act."),
        ("Contract Theory", "A contract is a legally binding document between at least two parties that defines and governs the rights and duties of the parties."),
        ("Intellectual Property", "Intellectual property is a category of property that includes intangible creations of the human intellect."),
        ("Habeas Corpus", "Habeas corpus is a recourse in law through which a person can report an unlawful detention or imprisonment to a court."),
        ("Double Jeopardy", "Double jeopardy is a procedural defence that prevents an accused person from being tried again on the same (or similar) charges."),
        ("Due Process", "Due process is the legal requirement that the state must respect all legal rights that are owed to a person."),
        ("NDA Agreements", "A non-disclosure agreement is a legal contract that outlines confidential material, knowledge, or information."),
        ("Class Action", "A class action is a type of lawsuit where one of the parties is a group of people who are represented collectively by a member of that group."),
        ("Liability Insurance", "Liability insurance is a part of the general insurance system of risk financing to protect the purchaser from the risks of liabilities imposed by lawsuits and similar claims."),
        ("Probate Law", "Probate is the judicial process whereby a will is 'proved' in a court of law and accepted as a valid public document.")
    ],
    "SCIFI": [
        ("Three Laws of Robotics", "A robot may not injure a human being or, through inaction, allow a human being to come to harm."),
        ("Warp Drive", "Warp drive is a fictitious faster-than-light (FTL) spacecraft propulsion system in many science fiction works, notably Star Trek."),
        ("Dyson Sphere", "A Dyson sphere is a hypothetical megastructure that completely encompasses a star and captures a large percentage of its solar power output."),
        ("Cyberpunk Genre", "Cyberpunk is a subgenre of science fiction in a dystopian futuristic setting that tends to focus on a combination of low-life and high tech."),
        ("Time Travel Paradox", "The grandfather paradox is a paradox of time travel in which inconsistencies emerge through changing the past."),
        ("Teleportation", "Teleportation is the hypothetical transfer of matter or energy from one point to another without traversing the physical space between them."),
        ("Alien Contact", "First contact is a common science fiction theme about the first meeting between humans and extraterrestrial life."),
        ("Artificial Superintelligence", "Superintelligence is a hypothetical agent that possesses intelligence far surpassing that of the brightest and most gifted human minds."),
        ("Galactic Empire", "A galactic empire is a common trope in science fiction, consisting of an empire that spans much or all of a galaxy."),
        ("Multiverse Theory", "The multiverse is a hypothetical group of multiple universes.")
    ]
}


def seed():
    print("="*60)
    print("SEEDING EXTENDED AUDIT DATA (50 Items)")
    print("="*60)
    
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    
    # Load Models ONCE
    print("--> Loading Models (This takes time, but happens only once)...")
    dense_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)
    sparse_model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    
    count = 0
    for cluster, items in CLUSTERS.items():
        print(f"--> Processing Cluster: {cluster}")
        for title, content in items:
            # Dense
            dense_vec = dense_model.encode(content).tolist()
            
            # Sparse
            sparse_out = sparse_model.encode(
                content,
                return_dense=False,
                return_sparse=True,
                return_colbert_vecs=False
            )
            sparse_vec = sparse_out['lexical_weights']
            
            res = Resource(
                title=title,
                description=content,
                embedding=dense_vec
                # sparse_embedding=json.dumps(sparse_vec),  # Uncomment if your model supports this
            )
            session.add(res)
            session.flush()
            
            # Create Annotation (Ground Truth)
            ann = Annotation(
                resource_id=res.id,
                text=title,  # The title is the query
                created_at=datetime.utcnow()
            )
            session.add(ann)
            count += 1
    
    session.commit()
    print(f"SUCCESS: Created {count} resources across 5 clusters.")


if __name__ == "__main__":
    seed()
