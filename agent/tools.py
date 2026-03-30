"""
Tools for the real estate marketing voice agent.
Features properties in Ahmedabad and Himmatnagar, Gujarat.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from agent.property_data import search_properties_by_query, format_property_result


class PropertySearchInput(BaseModel):
    """Input schema for property search tool."""
    query: str = Field(
        description="Natural language search query in Hindi, Gujarati, or English describing desired property features, "
                    "location preferences, budget, or amenities "
                    "(e.g., '3 BHK in Ahmedabad under 50 lakh', 'अहमदाबाद में 3 बीएचके फ्लैट', 'અમદાવાદમાં 3 BHK ફ્લેટ', or 'commercial shop in Himmatnagar')"
    )


class ScheduleVisitInput(BaseModel):
    """Input schema for scheduling a property visit."""
    date: str = Field(description="Preferred date for the visit (e.g., 'tomorrow', 'March 15', 'next Monday')")
    time: str = Field(description="Preferred time for the visit (e.g., '2pm', '10:00 AM', 'afternoon')")
    property_name: str = Field(description="Name of the property to visit (e.g., 'Shantiniketan Homes')")
    attendee_name: str = Field(description="Name of the person attending the visit")
    phone: str = Field(description="Contact phone number for confirmation")


@tool(args_schema=PropertySearchInput)
def search_properties(query: str) -> str:
    """
    Search available properties by description, location, features, or budget.
    Query can be in Hindi, Gujarati, or English.
    Use this when the user asks about properties, homes, houses, apartments, shops, offices, or mentions
    specific requirements like number of bedrooms, price range, location, or amenities.

    Returns formatted property listings with key details.
    """
    try:
        results = search_properties_by_query(query, k=4)

        if not results:
            return "I couldn't find any properties matching those specific criteria. " \
                   "But don't worry - we have several properties in Ahmedabad and Himmatnagar that might interest you! " \
                   "Could you tell me a bit more? Are you looking for residential (home/flat) or commercial property (shop/office)?"

        formatted = []
        for doc in results:
            formatted.append(format_property_result(doc))

        response = "Great news! I found some properties that match what you're looking for:\n\n"
        response += "\n---\n\n".join(formatted)
        response += "\n\nAny of these catch your eye? I'd love to tell you more about them, " \
                    "or we can schedule a visit if you'd like to see them in person!"

        return response

    except Exception:
        # Fallback with sample properties
        return "I'm having a bit of trouble searching right now, but we have great properties in Ahmedabad " \
               "(Gota, Vastrapur, Shela, Bopal, Chandkheda, GIFT City) and Himmatnagar. " \
               "Prices start from Rs. 18 lakhs for residential and Rs. 25 lakhs for commercial. " \
               "What kind of property are you looking for?"


@tool(args_schema=ScheduleVisitInput)
def schedule_visit(date: str, time: str, property_name: str, attendee_name: str, phone: str) -> str:
    """
    Schedule a property visit for a potential buyer.
    Use this when the user expresses interest in visiting a property and provides
    their preferred date, time, and contact information.

    Returns confirmation message with visit details.
    """
    # Mimic scheduling - in production this would integrate with a calendar system
    return (
        f"Perfect! I've got your visit scheduled. Here are the details:\n\n"
        f"📍 Property: {property_name}\n"
        f"📅 Date: {date}\n"
        f"⏰ Time: {time}\n"
        f"👤 Visitor: {attendee_name}\n"
        f"📞 Contact: {phone}\n\n"
        f"You'll receive a confirmation call shortly before your visit. "
        f"Our team is excited to show you around! If you need to reschedule, "
        f"just give us a call. Anything else I can help you with today?"
    )


@tool
def get_property_highlights(property_name: str = None) -> str:
    """
    Get highlights and special offers for properties.
    Use this when the user asks about deals, offers, discounts, or what makes
    a property special. If no property name is given, returns highlights from multiple properties.
    """
    highlights = {
        "Shantiniketan Homes": "RERA approved, possession in 2 years, bank loan available, newly launched",
        "Prajapati Sky Heights": "Prime Vastrapur location, lake view, limited units, VIP booking open",
        "Shivalik Serenity": "Near GIFT City, high rental yield, first home scheme eligible, stamp duty waiver",
        "Karma Lakeview Residency": "Lake facing, Italian marble, smart home ready, club membership included",
        "Sanskriti Township": "Affordable housing, PMAY benefits, metro nearby, quick possession",
        "Himmat Green Valley": "Hill view, pollution-free area, large plots, NRI-friendly",
        "Shivam Residency Himmatnagar": "Central location, all amenities nearby, ready to move, negotiable pricing",
        "Arvind Hillside Villas": "Hill facing, gated community, premium location, builder floor",
        "SG Highway Commercial Complex": "High visibility, metro connectivity, premium address, 8% rental yield",
        "Prahlad Nagar Business Hub": "Furnished option, IT park nearby, easy highway access, loan available",
        "Maninagar Retail Plaza": "High footfall, market area, immediate possession, investment opportunity",
        "GIFT City Tech Park": "Tax benefits, SEZ zone, global business hub, high appreciation potential",
        "Himmatnagar Market Shop": "Busy market, established area, good footfall, affordable",
        "Himmatnagar Industrial Shed": "GIDC approved, industrial area, large space, expansion possible",
    }

    if property_name:
        # Find matching property
        for name, highlight in highlights.items():
            if property_name.lower() in name.lower():
                return f"Here's what makes {name} special: {highlight}"

        return f"I'd love to tell you about {property_name}, but could you help me with the exact name? " \
               f"We have properties in Ahmedabad and Himmatnagar - which area interests you?"

    # Return highlights from featured properties (mix of residential and commercial)
    response = "Here are some exciting offers from our featured properties:\n\n"
    response += "🏠 Residential:\n"
    response += "• Shantiniketan Homes (Gota): RERA approved, bank loan available\n"
    response += "• Shivalik Serenity (Shela): Near GIFT City, stamp duty waiver\n"
    response += "• Himmat Green Valley (Himmatnagar): Hill view, pollution-free\n\n"
    response += "🏢 Commercial:\n"
    response += "• SG Highway Commercial Complex: Premium address, 8% rental yield\n"
    response += "• GIFT City Tech Park: Tax benefits, SEZ zone\n"
    response += "• Himmatnagar Market Shop: High footfall, affordable\n\n"
    response += "Any of these sound interesting? I can tell you more about any property that catches your attention!"
    return response


@tool
def ask_property_preference() -> str:
    """
    Ask the user about their property preference - residential (housing) or commercial.
    Use this at the start of conversation or when the user hasn't specified what type
    of property they're looking for.

    Returns a friendly question to understand user's needs.
    """
    return (
        "I'd love to help you find the perfect property! "
        "To get started, could you tell me - are you looking for:\n\n"
        "🏠 **Residential property** - like a 2BHK/3BHK flat, bungalow, or home for your family?\n\n"
        "🏢 **Commercial property** - like a shop, office space, or industrial shed for business?\n\n"
        "Also, which area do you prefer - Ahmedabad or Himmatnagar? "
        "And what's your approximate budget?"
    )


@tool
def get_area_info(area: str) -> str:
    """
    Get information about a specific area in Ahmedabad or Himmatnagar.
    Area name can be in Hindi, Gujarati, or English.
    Use this when the user asks about locations, neighborhoods, or which area to choose.
    """
    area_info = {
        "gota": "Gota is a fast-developing area on SG Highway, close to IT parks. Great for young professionals. Properties: Shantiniketan Homes.",
        "vastrapur": "Vastrapur is a premium central location near Vastrapur Lake, with great restaurants and schools. Properties: Prajapati Sky Heights.",
        "shela": "Shela is near GIFT City with high growth potential and affordable prices. Perfect for investors. Properties: Shivalik Serenity.",
        "bopal": "South Bopal is an upscale residential area with lake views and premium amenities. Properties: Karma Lakeview Residency.",
        "chandkheda": "Chandkheda offers affordable housing with metro connectivity and PMAY benefits. Properties: Sanskriti Township.",
        "gift city": "GIFT City is India's first smart city with tax benefits and SEZ advantages. Ideal for IT companies. Properties: GIFT City Tech Park.",
        "himmatnagar": "Himmatnagar is a peaceful hill station town, pollution-free and perfect for retirement or weekend homes. Properties: Himmat Green Valley, Shivam Residency.",
        "maninagar": "Maninagar is a busy traditional market area with high footfall for retail business. Properties: Maninagar Retail Plaza.",
        "prahlad nagar": "Prahlad Nagar is a business hub with modern offices and IT parks nearby. Properties: Prahlad Nagar Business Hub.",
        "sg highway": "SG Highway is Ahmedabad's premium business address with metro connectivity. Properties: SG Highway Commercial Complex.",
        "gidc": "GIDC Himmatnagar is the industrial estate suitable for manufacturing and warehousing. Properties: Himmatnagar Industrial Shed.",
        # Hindi variants
        "गोटा": "Gota - SG Highway के पास तेजी से विकसित क्षेत्र, IT पार्क के करीब। Shantiniketan Homes यहाँ है।",
        "वैष्णवदेवी": "Vastrapur - प्रीमियम सेंट्रल लोकेशन, Vastrapur Lake के पास। Prajapati Sky Heights यहाँ है।",
        "शेला": "Shela - GIFT City के पास, निवेश के लिए बेहतरीन। Shivalik Serenity यहाँ है।",
        "बोपाल": "South Bopal - झील के नज़ारे वाले प्रीमियम आवासीय क्षेत्र। Karma Lakeview Residency यहाँ है।",
        "चंदखेड़ा": "Chandkheda - किफायती आवास, मेट्रो कनेक्टिविटी। Sanskriti Township यहाँ है।",
        "गिफ्ट सिटी": "GIFT City - भारत का पहला स्मार्ट सिटी, टैक्स बेनिफिट के साथ। GIFT City Tech Park यहाँ है।",
        "हिम्मतनगर": "Himmatnagar - शांत हिल स्टेशन, प्रदूषण मुक्त। Himmat Green Valley और Shivam Residency यहाँ है।",
        "मणिनगर": "Maninagar - व्यस्त बाजार क्षेत्र, रिटेल के लिए बेहतरीन। Maninagar Retail Plaza यहाँ है।",
        # Gujarati variants
        "ગોટા": "Gota - SG Highway નજીક ઝડપી વિકસતું વિસ્તાર, IT પાર્કની નજીક. Shantiniketan Homes અહીં છે.",
        "વૈષ્ણવદેવી": "Vastrapur - પ્રીમિયમ સેન્ટ્રલ લોકેશન, Vastrapur લેકની નજીક. Prajapati Sky Heights અહીં છે.",
        "શેલા": "Shela - GIFT City ની નજીક, રોકાણ માટે શ્રેષ્ઠ. Shivalik Serenity અહીં છે.",
        "બોપાલ": "South Bopal - પ્રીમિયમ રેસિડેન્શિયલ વિસ્તાર, લેક વ્યૂ. Karma Lakeview Residency અહીં છે.",
        "ચંદખેડા": "Chandkheda - પરવડતું ઘર, મેટ્રો કનેક્ટિવિટી. Sanskriti Township અહીં છે.",
        "ગિફ્ટ સિટી": "GIFT City - ભારતનું પ્રથમ સ્માર્ટ સિટી, ટેક્સ લાભ સાથે. GIFT City Tech Park અહીં છે.",
        "હિંમતનગર": "Himmatnagar - શાંત હિલ સ્ટેશન, પ્રદૂષણ મુક્ત. Himmat Green Valley અને Shivam Residency અહીં છે.",
        "મણિનગર": "Maninagar - વ્યસ્ત બજાર વિસ્તાર, રિટેલ માટે શ્રેષ્ઠ. Maninagar Retail Plaza અહીં છે.",
    }

    area_lower = area.lower()
    for key, info in area_info.items():
        if key in area_lower:
            return info

    return (
        f"We have properties across Ahmedabad (Gota, Vastrapur, Shela, Bopal, Chandkheda, GIFT City, Maninagar, Prahlad Nagar, SG Highway) "
        f"and Himmatnagar. Each area has its own advantages! "
        f"Could you tell me more about what's important to you - proximity to work, schools, markets, or peaceful surroundings?"
    )
