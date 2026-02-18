"""
Load GraphRAG output into Neo4j database
Run after GraphRAG indexing completes
"""

import pandas as pd
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class GraphRAGToNeo4j:
    def __init__(self, uri, user, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✅ Connected to Neo4j at {uri}")

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        print("✅ Connection closed")

    def clear_database(self):
        """Clear all existing data (optional - use with caution!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Database cleared")

    def create_indexes(self):
        """Create indexes for better performance"""
        with self.driver.session() as session:
            # Create indexes
            session.run("CREATE INDEX entity_id IF NOT EXISTS FOR (e:Entity) ON (e.id)")
            session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            session.run("CREATE INDEX community_id IF NOT EXISTS FOR (c:Community) ON (c.id)")
        print("✅ Indexes created")

    def load_entities(self, parquet_path="output/create_final_nodes.parquet"):
        """Load entities/nodes from GraphRAG"""
        print(f"📥 Loading entities from {parquet_path}...")

        try:
            df = pd.read_parquet(parquet_path)
            print(f"   Found {len(df)} entities")

            with self.driver.session() as session:
                count = 0
                for _, row in df.iterrows():
                    session.run("""
                        MERGE (e:Entity {id: $id})
                        SET e.name = $name,
                            e.type = $type,
                            e.description = $description,
                            e.human_readable_id = $human_readable_id,
                            e.degree = $degree
                    """,
                    id=str(row.get('id', '')),
                    name=str(row.get('title', row.get('name', ''))),
                    type=str(row.get('type', 'Unknown')),
                    description=str(row.get('description', '')),
                    human_readable_id=str(row.get('human_readable_id', '')),
                    degree=int(row.get('degree', 0)) if pd.notna(row.get('degree')) else 0
                    )
                    count += 1
                    if count % 100 == 0:
                        print(f"   Loaded {count}/{len(df)} entities...")

            print(f"✅ Loaded {count} entities")
            return count
        except FileNotFoundError:
            print(f"❌ File not found: {parquet_path}")
            return 0
        except Exception as e:
            print(f"❌ Error loading entities: {e}")
            return 0

    def load_relationships(self, parquet_path="output/create_final_relationships.parquet"):
        """Load relationships/edges from GraphRAG"""
        print(f"📥 Loading relationships from {parquet_path}...")

        try:
            df = pd.read_parquet(parquet_path)
            print(f"   Found {len(df)} relationships")

            with self.driver.session() as session:
                count = 0
                for _, row in df.iterrows():
                    session.run("""
                        MATCH (source:Entity {id: $source_id})
                        MATCH (target:Entity {id: $target_id})
                        MERGE (source)-[r:RELATES_TO]->(target)
                        SET r.description = $description,
                            r.weight = $weight,
                            r.human_readable_id = $human_readable_id,
                            r.combined_degree = $combined_degree
                    """,
                    source_id=str(row.get('source', '')),
                    target_id=str(row.get('target', '')),
                    description=str(row.get('description', '')),
                    weight=float(row.get('weight', 1.0)) if pd.notna(row.get('weight')) else 1.0,
                    human_readable_id=str(row.get('human_readable_id', '')),
                    combined_degree=int(row.get('combined_degree', 0)) if pd.notna(row.get('combined_degree')) else 0
                    )
                    count += 1
                    if count % 100 == 0:
                        print(f"   Loaded {count}/{len(df)} relationships...")

            print(f"✅ Loaded {count} relationships")
            return count
        except FileNotFoundError:
            print(f"❌ File not found: {parquet_path}")
            return 0
        except Exception as e:
            print(f"❌ Error loading relationships: {e}")
            return 0

    def load_communities(self, parquet_path="output/create_final_communities.parquet"):
        """Load community clusters from GraphRAG"""
        print(f"📥 Loading communities from {parquet_path}...")

        try:
            df = pd.read_parquet(parquet_path)
            print(f"   Found {len(df)} communities")

            with self.driver.session() as session:
                count = 0
                for _, row in df.iterrows():
                    # Create community node
                    session.run("""
                        MERGE (c:Community {id: $id})
                        SET c.title = $title,
                            c.level = $level,
                            c.size = $size
                    """,
                    id=str(row.get('id', '')),
                    title=str(row.get('title', '')),
                    level=int(row.get('level', 0)) if pd.notna(row.get('level')) else 0,
                    size=int(row.get('size', 0)) if pd.notna(row.get('size')) else 0
                    )
                    count += 1
                    if count % 50 == 0:
                        print(f"   Loaded {count}/{len(df)} communities...")

            print(f"✅ Loaded {count} communities")
            return count
        except FileNotFoundError:
            print(f"❌ File not found: {parquet_path}")
            return 0
        except Exception as e:
            print(f"❌ Error loading communities: {e}")
            return 0

    def load_all(self):
        """Load all GraphRAG data into Neo4j"""
        print("\n" + "="*60)
        print("Loading GraphRAG data into Neo4j...")
        print("="*60 + "\n")

        # Create indexes first
        self.create_indexes()

        # Load data
        entities = self.load_entities()
        relationships = self.load_relationships()
        communities = self.load_communities()

        print("\n" + "="*60)
        print("SUMMARY:")
        print(f"  Entities: {entities}")
        print(f"  Relationships: {relationships}")
        print(f"  Communities: {communities}")
        print("="*60 + "\n")

        if entities > 0:
            print("✅ Data loaded successfully!")
            print("\nYou can now:")
            print("  1. Open Neo4j Browser: http://localhost:7474")
            print("  2. Run Cypher queries")
            print("  3. Visualize the knowledge graph")
        else:
            print("⚠️  No entities loaded. Make sure GraphRAG indexing completed.")
            print("   Run: python -m graphrag index --root .")


# Main execution
if __name__ == "__main__":
    # Neo4j connection details
    # Update these with your Neo4j credentials
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")  # CHANGE THIS!

    print("Neo4j Connection:")
    print(f"  URI: {NEO4J_URI}")
    print(f"  User: {NEO4J_USER}")
    print()

    # Ask for confirmation
    response = input("⚠️  This will load data into Neo4j. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        exit(0)

    # Load data
    loader = GraphRAGToNeo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # Optional: Clear existing data (uncomment if needed)
        # clear = input("Clear existing data? (y/n): ")
        # if clear.lower() == 'y':
        #     loader.clear_database()

        loader.load_all()
    finally:
        loader.close()

    print("\n✅ Done! Open Neo4j Browser to explore the graph.")
