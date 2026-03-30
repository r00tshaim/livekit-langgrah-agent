"""
Property campaign data and ChromaDB vector store initialization.
Features properties in Ahmedabad and Himmatnagar, Gujarat - both residential and commercial.
"""

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Property campaign data for Ahmedabad and Himmatnagar, Gujarat
# Includes both residential (housing) and commercial properties
PROPERTIES = [
    # ========== RESIDENTIAL PROPERTIES - AHMEDABAD ==========
    {
        "id": "AH001",
        "name": "Shantiniketan Homes",
        "location": "Gota, Ahmedabad",
        "type": "residential",
        "price": 4500000,
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft": 1650,
        "description": "Spacious 3BHK apartments in Gota with modern amenities. Close to SG Highway, perfect for IT professionals and families.",
        "amenities": ["swimming pool", "gymnasium", "children's play area", "24/7 security", "covered parking", "clubhouse"],
        "highlights": ["Newly launched", "RERA approved", "Possession in 2 years", "Bank loan available"],
    },
    {
        "id": "AH002",
        "name": "Prajapati Sky Heights",
        "location": "Vastrapur, Ahmedabad",
        "type": "residential",
        "price": 7500000,
        "bedrooms": 4,
        "bathrooms": 3,
        "sqft": 2400,
        "description": "Premium 4BHK luxury apartments in heart of Vastrapur. Walking distance to Vastrapur Lake and BRTS.",
        "amenities": ["rooftop garden", "fitness center", "party plot", "concierge", "power backup", "lift"],
        "highlights": ["Prime location", "Lake view", "Limited units", "VIP booking open"],
    },
    {
        "id": "AH003",
        "name": "Shivalik Serenity",
        "location": "Shela, Ahmedabad",
        "type": "residential",
        "price": 3200000,
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 1200,
        "description": "Affordable 2BHK homes in Shela near GIFT City. Ideal for young professionals and investors.",
        "amenities": ["community center", "jogging track", "yoga lawn", "security", "rainwater harvesting"],
        "highlights": ["Near GIFT City", "High rental yield potential", "First home scheme eligible", "Stamp duty waiver"],
    },
    {
        "id": "AH004",
        "name": "Karma Lakeview Residency",
        "location": "South Bopal, Ahmedabad",
        "type": "residential",
        "price": 5800000,
        "bedrooms": 3,
        "bathrooms": 3,
        "sqft": 1950,
        "description": "Luxury 3BHK with lake views in South Bopal. Premium finishes and world-class amenities.",
        "amenities": ["infinity pool", "spa", "tennis court", "cricket practice area", "multipurpose hall", "landscaped gardens"],
        "highlights": ["Lake facing", "Italian marble", "Smart home ready", "Club membership included"],
    },
    {
        "id": "AH005",
        "name": "Sanskriti Township",
        "location": "Chandkheda, Ahmedabad",
        "type": "residential",
        "price": 2800000,
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 1100,
        "description": "Budget-friendly 2BHK apartments in Chandkheda. Perfect for first-time homebuyers.",
        "amenities": ["playground", "gym", "security", "parking", "water supply 24/7"],
        "highlights": ["Affordable housing", "PMAY benefits", "Metro nearby", "Quick possession"],
    },

    # ========== RESIDENTIAL PROPERTIES - HIMMATNAGAR ==========
    {
        "id": "HM001",
        "name": "Himmat Green Valley",
        "location": "Himmatnagar, Gujarat",
        "type": "residential",
        "price": 1800000,
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft": 1400,
        "description": "Peaceful 3BHK bungalows in Himmatnagar with lush green surroundings. Perfect for retirement or weekend home.",
        "amenities": ["garden area", "parking", "security", "temple", "community hall"],
        "highlights": ["Hill view", "Pollution-free area", "Large plots", "NRI-friendly"],
    },
    {
        "id": "HM002",
        "name": "Shivam Residency Himmatnagar",
        "location": "Station Road, Himmatnagar",
        "type": "residential",
        "price": 2200000,
        "bedrooms": 2,
        "bathrooms": 2,
        "sqft": 1150,
        "description": "Modern 2BHK apartments in central Himmatnagar. Close to market, schools, and hospitals.",
        "amenities": ["lift", "power backup", "security", "parking", "water storage"],
        "highlights": ["Central location", "All amenities nearby", "Ready to move", "Negotiable pricing"],
    },
    {
        "id": "HM003",
        "name": "Arvind Hillside Villas",
        "location": "Hathijan, Himmatnagar",
        "type": "residential",
        "price": 3500000,
        "bedrooms": 4,
        "bathrooms": 3,
        "sqft": 2200,
        "description": "Luxury villas with hill views in Hathijan. Spacious homes for growing families.",
        "amenities": ["private garden", "terrace", "parking for 2 cars", "servant room", "modular kitchen"],
        "highlights": ["Hill facing", "Gated community", "Premium location", "Builder floor"],
    },

    # ========== COMMERCIAL PROPERTIES - AHMEDABAD ==========
    {
        "id": "AC001",
        "name": "SG Highway Commercial Complex",
        "location": "SG Highway, Ahmedabad",
        "type": "commercial",
        "price": 12000000,
        "sqft": 2500,
        "description": "Prime commercial office space on SG Highway. Ideal for corporate offices, banks, or showrooms.",
        "amenities": ["central AC", "high-speed elevators", "24/7 power backup", "security", "parking", "food court"],
        "highlights": ["High visibility", "Metro connectivity", "Premium address", "Rental yield 8%"],
    },
    {
        "id": "AC002",
        "name": "Prahlad Nagar Business Hub",
        "location": "Prahlad Nagar, Ahmedabad",
        "type": "commercial",
        "price": 8500000,
        "sqft": 1800,
        "description": "Modern office space in Prahlad Nagar business district. Perfect for startups and SMEs.",
        "amenities": ["conference room", "reception area", "pantry", "lift", "security", "CCTV"],
        "highlights": ["Furnished option", "IT park nearby", "Easy highway access", "Loan available"],
    },
    {
        "id": "AC003",
        "name": "Maninagar Retail Plaza",
        "location": "Maninagar, Ahmedabad",
        "type": "commercial",
        "price": 5500000,
        "sqft": 1200,
        "description": "Retail shop in busy Maninagar market area. High footfall location for retail business.",
        "amenities": ["ground floor", "glass facade", "AC ready", "parking", "security"],
        "highlights": ["High footfall", "Market area", "Immediate possession", "Investment opportunity"],
    },
    {
        "id": "AC004",
        "name": "GIFT City Tech Park",
        "location": "GIFT City, Ahmedabad",
        "type": "commercial",
        "price": 18000000,
        "sqft": 3200,
        "description": "Premium office space in GIFT City - India's first smart city. Ideal for IT/ITeS companies.",
        "amenities": ["smart building", "high-speed internet", "central AC", "cafeteria", "gym", "conference facilities"],
        "highlights": ["Tax benefits", "SEZ zone", "Global business hub", "Appreciation potential"],
    },

    # ========== COMMERCIAL PROPERTIES - HIMMATNAGAR ==========
    {
        "id": "HC001",
        "name": "Himmatnagar Market Shop",
        "location": "Main Market, Himmatnagar",
        "type": "commercial",
        "price": 2500000,
        "sqft": 600,
        "description": "Retail shop in main Himmatnagar market. Perfect for clothing, electronics, or general store.",
        "amenities": ["ground floor", "shutter", "electricity", "water", "parking nearby"],
        "highlights": ["Busy market", "Established area", "Good footfall", "Affordable"],
    },
    {
        "id": "HC002",
        "name": "Himmatnagar Industrial Shed",
        "location": "GIDC, Himmatnagar",
        "type": "commercial",
        "price": 6000000,
        "sqft": 5000,
        "description": "Industrial shed in GIDC estate. Suitable for manufacturing, warehousing, or godown.",
        "amenities": ["three-phase power", "water connection", "loading bay", "security", "road access"],
        "highlights": ["GIDC approved", "Industrial area", "Large space", "Expansion possible"],
    },
]


def create_property_documents() -> list[Document]:
    """Convert property data to LangChain documents for vector store."""
    documents = []
    for prop in PROPERTIES:
        # Create a rich text representation for embedding
        property_type = prop.get("type", "residential")
        type_label = "Residential" if property_type == "residential" else "Commercial"

        content = f"""
        Type: {type_label}
        Property: {prop['name']}
        Location: {prop['location']}
        Price: Rs. {prop['price']:,}
        Size: {prop['sqft']} sqft
        """.strip()

        if property_type == "residential":
            content += f"""
        Bedrooms: {prop['bedrooms']} BHK
        Bathrooms: {prop['bathrooms']}
        """.strip()

        content += f"""
        Description: {prop['description']}
        Amenities: {', '.join(prop['amenities'])}
        Highlights: {', '.join(prop['highlights'])}
        """.strip()

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "id": prop["id"],
                    "name": prop["name"],
                    "location": prop["location"],
                    "price": prop["price"],
                    "type": property_type,
                    "sqft": prop["sqft"],
                    "bedrooms": prop.get("bedrooms", None),
                    "bathrooms": prop.get("bathrooms", None),
                },
            )
        )
    return documents


def initialize_vector_store() -> Chroma:
    """
    Initialize ChromaDB vector store with property data.
    Uses OpenAI embeddings for semantic similarity search.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    documents = create_property_documents()

    # Create vector store from documents
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="./chroma_property_db",  # Persistent storage
        collection_name="gujarat_properties",
    )

    return vectorstore


# Global vector store instance (initialized on first use)
_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    """Get or create the property vector store."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = initialize_vector_store()
    return _vectorstore


def search_properties_by_query(query: str, k: int = 4) -> list[Document]:
    """
    Search properties using semantic similarity.

    Args:
        query: Natural language search query (e.g., "3 BHK in Ahmedabad under 50 lakh" or "commercial shop in Himmatnagar")
        k: Number of results to return

    Returns:
        List of matching property documents
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return results


def format_property_result(doc: Document) -> str:
    """Format a property document for display to the user."""
    meta = doc.metadata
    property_type = meta.get("type", "residential")
    type_emoji = "🏠" if property_type == "residential" else "🏢"

    lines = [f"{type_emoji} {meta['name']} ({meta['id']})"]
    lines.append(f"📍 Location: {meta['location']}")
    lines.append(f"💰 Price: Rs. {meta['price']:,}")
    lines.append(f"📐 Size: {meta['sqft']} sqft")

    if meta.get("bedrooms"):
        lines.append(f"🛏️ {meta['bedrooms']} BHK")
    if meta.get("bathrooms"):
        lines.append(f"🚿 {meta['bathrooms']} bathrooms")

    # Extract description from page_content
    content = doc.page_content
    if "Description:" in content:
        desc = content.split("Description:")[1].split("\n")[0].strip()
        lines.append(f"\n📝 {desc}")

    return "\n".join(lines)


