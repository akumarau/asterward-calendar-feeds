#!/usr/bin/env python3
"""Build Japan Trip 2026 .ics for Outlook import."""
import os
from datetime import datetime, timezone

TOK = "Asia/Tokyo"
SYD = "Australia/Sydney"
NOW = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# ---------- Locations ----------
L = {
    "SYD": "Sydney Airport T1 International, Mascot NSW 2020, Australia",
    "HND3": "Haneda Airport Terminal 3, 2-6-5 Hanedakuko, Ota City, Tokyo 144-0041, Japan",
    "HND1": "Haneda Airport Terminal 1, 3-3-2 Hanedakuko, Ota City, Tokyo 144-0041, Japan",
    "HIJ": "Hiroshima Airport, 64-31 Zennyuji, Hongo-cho, Mihara, Hiroshima 729-0416, Japan",
    "NIPPORI_STN": "Nippori Station West Exit, Arakawa City, Tokyo, Japan",
    "SAKURA": "Sakura Hotel Nippori, 3 Chome-43-15 Sendagi, Bunkyo City, Tokyo 113-0022, Japan",
    "GAKU": "Hakone Guesthouse Gaku, 1380-385 Gora, Hakone, Kanagawa 250-0408, Japan",
    "ZENKOJI": "Temple Hotel Takayama Zenkoji, 4-3 Tenmanmachi, Takayama, Gifu 506-0025, Japan",
    "GION": "Ryokan Hostel Gion, 391-2 Motomachi, Higashiyama Ward, Kyoto 605-0089, Japan",
    "LINKS": "Hotel Links Namba, 1-9-27 Inari, Naniwa Ward, Osaka 556-0023, Japan",
    "FUGEN": "Fugen In Temple (Shukubo Fugenin), 605 Koyasan, Koya, Ito District, Wakayama 648-0211, Japan",
    "KURETAKE": "Hotel Kuretakeso Hiroshima Otemachi, 3-7-3 Otemachi, Naka Ward, Hiroshima 730-0051, Japan",
    "SUPER": "Super Hotel Mihara Ekimae, 1-12-10 Shiromachi, Mihara, Hiroshima, Japan",
    "MIHARA_STN": "JR Mihara Station, 1 Chome Shiromachi, Mihara, Hiroshima, Japan",
}

# ---------- Data ----------
# All day summaries: (date, title, location, description)
ALLDAY = [
    ("20261115", "Japan D0 | Fly Sydney to Tokyo", L["SAKURA"],
     "QF59 Sydney 12:00 to Haneda T3 20:00 (local).\n"
     "Night: Sakura Hotel Nippori (pre tour night, booked 15 to 16 Nov). Check in from 15:00.\n"
     "Transfer: Monorail to Hamamatsucho, JR Yamanote to Nippori West Exit, about 1 hour."),
    ("20261116", "Japan D1 | Tokyo: tour starts 18:00, welcome dinner, Sensoji at night", L["SAKURA"],
     "One Life Adventures Japan Classic 14 Day.\n"
     "Meals included: dinner.\nOptional: Tokyo Skytree.\n"
     "Night: Sakura Hotel Nippori.\nKit: 24-70 + 12-24.\n"
     "Bring travel insurance proof for the guide."),
    ("20261117", "Japan D2 | Tokyo: Harajuku, Meiji Jingu, Akihabara", L["SAKURA"],
     "Meals included: breakfast.\nOptional: maid cafe in Akihabara.\n"
     "Night: Sakura Hotel Nippori.\nKit: 24-70 + 12-24."),
    ("20261118", "Japan D3 | Tokyo: sushi class, Shinjuku, Omoide Yokocho, Shibuya", L["SAKURA"],
     "Meals included: breakfast, lunch.\nOptional: Toyosu Fish Market, temple printed as 'Songokuji'.\n"
     "Night: Sakura Hotel Nippori.\nKit: 24-70 + 12-24. Best night street day."),
    ("20261119", "Japan D4 | Hakone: Romancecar, Mount Fuji views, nabe dinner", L["GAKU"],
     "Meals included: breakfast, dinner.\nNight: Gora Gaku Guesthouse, tatami twin or triple.\n"
     "Kit: 24-70 + 70-200 for Fuji compression.\n"
     "Expect 2 to 7 C in the morning. Owakudani has a respiratory caution."),
    ("20261120", "Japan D5 | Takayama: Shinkansen, old town, sake tasting, temple stay", L["ZENKOJI"],
     "Meals included: none.\nOptional: onsen or public bath.\n"
     "Night: Temple Hotel Takayama Zenkoji, multi share.\nKit: 24-70 + 12-24.\n"
     "Coldest stop: 0 to 5 C mornings, frost possible."),
    ("20261121", "Japan D6 | Takayama market, train to Kyoto, Gion walk", L["GION"],
     "Meals included: none.\nNight: Ryokan Hostel Gion, individual pod. Check in from 16:00.\n"
     "Kit: 24-70."),
    ("20261122", "Japan D7 | Kyoto: Fushimi Inari at dawn, Kiyomizudera, tea ceremony", L["GION"],
     "Meals included: none.\nOptional: Nishiki Market, kimono hire, geisha arts performance.\n"
     "Kendo may move to this day.\nNight: Ryokan Hostel Gion.\nKit: 12-24 + 24-70. No tripods at Kiyomizudera."),
    ("20261123", "Japan D8 | Kyoto: Kinkakuji, Daitokuji Zen gardens, kendo", L["GION"],
     "Meals included: none.\nOptional: Heian Shrine.\n"
     "23 Nov is a Japanese public holiday, expect crowds.\nNight: Ryokan Hostel Gion.\nKit: 24-70 + 70-200."),
    ("20261124", "Japan D9 | Arashiyama bamboo, monkeys, boat ride, Osaka Dotonbori", L["LINKS"],
     "Meals included: dinner.\nOptional: extended karaoke.\n"
     "Night: Hotel Links Namba, twin share (operator PDF, 'or similar').\n"
     "Kit: 24-70 + 70-200. Add 12-24 for the bamboo grove if you can carry it."),
    ("20261125", "Japan D10 | Osaka: free morning, Osaka Castle, Shinsekai", L["LINKS"],
     "Meals included: breakfast.\nOptional: Shinsaibashi, Amerikamura, Den Den Town, Spa World.\n"
     "Night: Hotel Links Namba.\nKit: 24-70 + 70-200."),
    ("20261126", "Japan D11 | Nara Park, then Koyasan temple stay", L["FUGEN"],
     "Meals included: breakfast, vegetarian temple dinner.\n"
     "Night: Fugen In Temple, tatami twin (operator PDF, 'or similar').\n"
     "Kit: 24-70 + 70-200 for the deer. Koyasan mornings 0 to 4 C."),
    ("20261127", "Japan D12 | Koyasan prayers, Danjo Garan, Shinkansen to Hiroshima, Peace Memorial", L["KURETAKE"],
     "Meals included: breakfast.\nNight: Hotel Kuretakeso Otemachi, twin room. Check in from 15:00.\n"
     "Kit: 24-70. Keep it respectful at the memorial."),
    ("20261128", "Japan D13 | Miyajima: Great Torii, Itsukushima Shrine, farewell evening", L["KURETAKE"],
     "Meals included: breakfast. Farewell meal not included.\n"
     "Night: Hotel Kuretakeso Otemachi.\nKit: 24-70 + 70-200."),
    ("20261129", "Japan D14 | Tour ends 09:00, Mihara, Buttsuji autumn leaves", L["SUPER"],
     "Meals included: breakfast (tour hotel).\n"
     "Night: Super Hotel Mihara Ekimae. Confirmed. Check in 15:00 to 23:00, check out by 10:00.\n"
     "Hotel phone +81 848 89 9000. Breakfast included at Super Hotel.\n"
     "Kit: 24-70 + 70-200 at Buttsuji."),
    ("20261130", "Japan D15 | Mount Fudekage sunrise, fly Hiroshima to Haneda to Sydney", L["HIJ"],
     "JL264 Hiroshima 17:55 to Haneda T1 19:15, then QF60 Haneda T3 22:00 to Sydney T1 10:00 (1 Dec).\n"
     "Overnight flight, no hotel."),
    ("20261201", "Back in Sydney | QF60 lands 10:00", L["SYD"],
     "QF60 arrives Sydney T1 at 10:00 local (updated from 09:55)."),
]

# Timed: (date, start, end, title, location_key_or_text, description, start_tz, end_tz, end_date)
T = []
def ev(date, s, e, title, loc, desc="", stz=TOK, etz=None, edate=None):
    T.append((date, s, e, title, L.get(loc, loc), desc, stz, etz or stz, edate or date))

# D0 Sun 15 Nov
ev("20261115", "0900", "1115", "Sydney Airport check in and security", "SYD",
   "QF59 departs 12:00. Seat not yet assigned.\nSpare batteries and power bank go in cabin bags.", stz=SYD)
ev("20261115", "1200", "2000", "✈ QF59 SYD 12:00 → HND 20:00", "SYD",
   "Qantas QF59. Sydney T1 to Tokyo Haneda T3.\n"
   "Departs 12:00 Sydney time, arrives 20:00 Tokyo time. 10 h, 7,816 km.\n"
   "Arrival gate forecast 141 to 148.", stz=SYD, etz=TOK)
ev("20261115", "2000", "2100", "Haneda arrival: immigration, customs, baggage", "HND3",
   "Have the Visit Japan Web QR codes ready.")
ev("20261115", "2100", "2215", "Transfer Haneda to Nippori", "NIPPORI_STN",
   "Tokyo Monorail to Hamamatsucho, JR Yamanote Line to Nippori, West Exit.\n"
   "Walk about 8 min (600 m) to the hotel. Around 1 hour in total.\n"
   "Operator PDF lists last trains around 23:09, check on the day. Taxi is the fallback.")
ev("20261115", "2215", "2245", "Check in: Sakura Hotel Nippori", "SAKURA",
   "Pre tour night booked 15 to 16 Nov. The tour uses this hotel from 16 Nov.\n"
   "Confirm at reception that your tour nights follow on, so you stay put.")

# D1 Mon 16 Nov
ev("20261116", "1000", "1300", "Tokyo Skytree (optional)", "Tokyo Skytree, 1 Chome-1-2 Oshiage, Sumida City, Tokyo 131-0045, Japan",
   "Listed optional for Day 1. Self funded. Daytime visit before the tour starts.")
ev("20261116", "1800", "1830", "Tour group meeting, hotel lobby", "SAKURA",
   "One Life Adventures. Guide meets the group in the lobby.\nBring insurance proof.")
ev("20261116", "1830", "2030", "Welcome dinner (included)", "Tokyo, venue set by guide")
ev("20261116", "2030", "2200", "Sensoji at night", "Sensoji, 2 Chome-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
   "Lenses: 12-24 for the gate and pagoda, 24-70 for the lanes.")

# D2 Tue 17 Nov
ev("20261117", "0730", "0830", "Breakfast (included)", "SAKURA")
ev("20261117", "0900", "1000", "Japan orientation", "Tokyo, set by guide")
ev("20261117", "1030", "1200", "Harajuku and Takeshita Street", "Takeshita Street, 1 Chome Jingumae, Shibuya City, Tokyo 150-0001, Japan")
ev("20261117", "1200", "1430", "Yoyogi Park and Meiji Jingu", "Meiji Jingu, 1-1 Yoyogikamizonocho, Shibuya City, Tokyo 151-8557, Japan")
ev("20261117", "1530", "1830", "Akihabara", "Akihabara Electric Town, Sotokanda, Chiyoda City, Tokyo 101-0021, Japan",
   "Neon and street. Sunset about 16:33.")
ev("20261117", "1830", "2000", "Maid cafe (optional)", "Akihabara, Chiyoda City, Tokyo, Japan")

# D3 Wed 18 Nov
ev("20261118", "0500", "0730", "Toyosu Fish Market (optional)", "Toyosu Market, 6 Chome-6-1 Toyosu, Koto City, Tokyo 135-0061, Japan",
   "Tuna auction runs early. Check viewing deck access and be back for breakfast.")
ev("20261118", "0800", "0900", "Breakfast (included)", "SAKURA")
ev("20261118", "1000", "1300", "Sushi making class and lunch (included)", "Tokyo, venue set by guide",
   "Send your sushi option to the operator by 9 Nov:\n"
   "1 raw fish sushi + cooked fish teriyaki\n2 vegetarian sushi + tofu teriyaki\n3 vegetarian sushi + cooked fish teriyaki")
ev("20261118", "1400", "1530", "Temple listed as 'Songokuji' (optional)", "Tokyo, confirm with guide",
   "Name as printed in the operator PDF. Confirm the actual temple with the guide.")
ev("20261118", "1600", "1730", "Shinjuku skyline at sunset", "Nishi Shinjuku, Shinjuku City, Tokyo, Japan",
   "Sunset about 16:32. Blue hour follows.")
ev("20261118", "1730", "1900", "Omoide Yokocho", "Omoide Yokocho, 1 Chome-2 Nishishinjuku, Shinjuku City, Tokyo 160-0023, Japan")
ev("20261118", "1930", "2100", "Shibuya Crossing", "Shibuya Scramble Crossing, 2 Chome-2-1 Dogenzaka, Shibuya City, Tokyo 150-0043, Japan",
   "Try 1/250 s to freeze people, 1/15 to 1/30 s for motion blur.")

# D4 Thu 19 Nov
ev("20261119", "0700", "0800", "Breakfast (included) and check out", "SAKURA")
ev("20261119", "0830", "1030", "Romancecar Shinjuku to Hakone Yumoto", "Shinjuku Station (Odakyu Line), Shinjuku City, Tokyo, Japan",
   "Ride is about 85 min.")
ev("20261119", "1030", "1600", "Hakone loop and Mount Fuji viewpoints", "Owakudani, 1251 Sengokuhara, Hakone, Kanagawa 250-0631, Japan",
   "Varied local transport: mountain train, cable car, ropeway, Lake Ashi.\n"
   "Fuji views are weather dependent, mornings are usually clearest.\n"
   "Owakudani has a respiratory caution. The operator has an alternate if needed.")
ev("20261119", "1630", "1700", "Check in: Gora Gaku Guesthouse", "GAKU")
ev("20261119", "1830", "2100", "Family nabe dinner and games (included)", "GAKU")

# D5 Fri 20 Nov
ev("20261120", "0700", "0745", "Check out: Gora Gaku Guesthouse", "GAKU")
ev("20261120", "0800", "1330", "Shinkansen and train: Hakone to Takayama", "Odawara Station, Odawara, Kanagawa, Japan",
   "First Shinkansen of the trip. Likely Odawara to Nagoya, then Limited Express Hida to Takayama.\n"
   "About 5 hours. Heading west, Fuji is on the right side (E seats) if clear.")
ev("20261120", "1400", "1630", "Takayama old town guided tour", "Sanmachi Suji, Kamisannomachi, Takayama, Gifu 506-0846, Japan")
ev("20261120", "1630", "1730", "Sake brewery tasting", "Sanmachi Suji breweries, Takayama, Gifu, Japan")
ev("20261120", "1730", "1800", "Check in: Temple Hotel Takayama Zenkoji", "ZENKOJI")
ev("20261120", "1830", "2000", "Dinner (self funded): try Hida beef", "Takayama old town, Gifu, Japan")
ev("20261120", "2000", "2100", "Onsen or public bath (optional)", "Takayama, Gifu, Japan",
   "Tattoo rules and washing etiquette apply.")

# D6 Sat 21 Nov
ev("20261121", "0700", "0830", "Miyagawa Morning Market", "Miyagawa Morning Market, Shimosannomachi, Takayama, Gifu, Japan")
ev("20261121", "0900", "0930", "Check out: Temple Hotel Takayama Zenkoji", "ZENKOJI")
ev("20261121", "0945", "1400", "Train: Takayama to Kyoto", "Takayama Station, Takayama, Gifu, Japan",
   "Limited Express Hida, likely via Nagoya and Shinkansen. About 4 hours.")
ev("20261121", "1430", "1500", "Drop bags: Ryokan Hostel Gion", "GION", "Check in opens 16:00.")
ev("20261121", "1700", "1900", "Guided Gion walking tour", "Hanamikoji Street, Gionmachi Minamigawa, Higashiyama Ward, Kyoto 605-0074, Japan",
   "Shoot geiko and maiko only from a respectful distance. 70-200 helps.")
ev("20261121", "1900", "2030", "Dinner (self funded)", "Pontocho, Nakagyo Ward, Kyoto, Japan")

# D7 Sun 22 Nov
ev("20261122", "0530", "0830", "Fushimi Inari Taisha before dawn", "Fushimi Inari Taisha, 68 Fukakusa Yabunouchicho, Fushimi Ward, Kyoto 612-0882, Japan",
   "Subway before dawn. Sunrise about 06:40. Do not block the paths.\nLens: 12-24 at f/4 to f/5.6.")
ev("20261122", "0930", "1130", "Kiyomizudera", "Kiyomizudera, 1 Chome-294 Kiyomizu, Higashiyama Ward, Kyoto 605-0862, Japan",
   "Tripods and monopods are prohibited.")
ev("20261122", "1200", "1300", "Tea ceremony", "Kyoto, venue set by guide")
ev("20261122", "1330", "1500", "Nishiki Market and lunch (optional)", "Nishiki Market, Nishikikoji Street, Nakagyo Ward, Kyoto 604-8055, Japan")
ev("20261122", "1500", "1800", "Kimono hire walk (optional)", "Higashiyama, Kyoto, Japan",
   "Sunset about 16:45.")
ev("20261122", "1900", "2000", "Geisha arts performance (optional)", "Gion Corner, 570-2 Gionmachi Minamigawa, Higashiyama Ward, Kyoto 605-0074, Japan",
   "Venue to confirm with the guide. Gion Corner is the usual option.")

# D8 Mon 23 Nov
ev("20261123", "0900", "1030", "Kinkakuji (Golden Pavilion)", "Kinkakuji, 1 Kinkakujicho, Kita Ward, Kyoto 603-8361, Japan",
   "CPL helps with reflections.")
ev("20261123", "1100", "1230", "Daitokuji Zen gardens", "Daitokuji, 53 Murasakino Daitokujicho, Kita Ward, Kyoto 603-8231, Japan")
ev("20261123", "1330", "1430", "Heian Shrine (optional)", "Heian Shrine, 97 Okazaki Nishitennocho, Sakyo Ward, Kyoto 606-8341, Japan")
ev("20261123", "1500", "1700", "Kendo class", "Kyoto, venue set by guide",
   "May swap with Day 7.")

# D9 Tue 24 Nov
ev("20261124", "0730", "0800", "Check out: Ryokan Hostel Gion", "GION")
ev("20261124", "0800", "0845", "Train to Arashiyama", "Arashiyama, Ukyo Ward, Kyoto, Japan")
ev("20261124", "0845", "1015", "Arashiyama Bamboo Grove", "Arashiyama Bamboo Grove, Sagaogurayama Tabuchiyamacho, Ukyo Ward, Kyoto 616-8394, Japan",
   "Watch vertical lines with the 12-24.")
ev("20261124", "1030", "1200", "Iwatayama Monkey Park", "Iwatayama Monkey Park, 8 Arashiyama Genrokuzancho, Nishikyo Ward, Kyoto 616-0004, Japan",
   "Keep more than 2 m from the monkeys. 70-200 is the lens.")
ev("20261124", "1230", "1400", "Traditional valley boat ride", "Arashiyama, Oi River near Togetsukyo Bridge, Kyoto, Japan",
   "Exact route set by the guide.")
ev("20261124", "1430", "1600", "Train to Osaka, check in: Hotel Links Namba", "LINKS",
   "Check in from 15:00.")
ev("20261124", "1800", "2030", "Dotonbori food tour (dinner included)", "Dotonbori, 1 Chome Dotonbori, Chuo Ward, Osaka 542-0071, Japan")
ev("20261124", "2030", "2230", "Karaoke, extended (optional)", "Namba, Osaka, Japan")

# D10 Wed 25 Nov
ev("20261125", "0800", "0900", "Breakfast (included)", "LINKS")
ev("20261125", "0930", "1130", "Shinsaibashi and Amerikamura (optional)", "Shinsaibashisuji, Chuo Ward, Osaka 542-0085, Japan")
ev("20261125", "1200", "1330", "Den Den Town (optional)", "Den Den Town, Nipponbashi, Naniwa Ward, Osaka 556-0005, Japan")
ev("20261125", "1345", "1545", "Spa World (optional)", "Spa World, 3 Chome-4-24 Ebisuhigashi, Naniwa Ward, Osaka 556-0002, Japan",
   "Tattoo rules apply.")
ev("20261125", "1615", "1800", "Osaka Castle Gardens", "Osaka Castle, 1-1 Osakajo, Chuo Ward, Osaka 540-0002, Japan",
   "Sunset about 16:50.")
ev("20261125", "1830", "2100", "Shinsekai evening tour and dinner (self funded)", "Shinsekai, Ebisuhigashi, Naniwa Ward, Osaka 556-0002, Japan")

# D11 Thu 26 Nov
ev("20261126", "0645", "0730", "Breakfast (included) and check out", "LINKS")
ev("20261126", "0745", "0830", "Train: Osaka to Nara", "Nara, Japan", "About 45 min.")
ev("20261126", "0830", "1230", "Nara Park and temples", "Nara Park, Zoshicho, Nara 630-8211, Japan",
   "Deer portraits with the 70-200.")
ev("20261126", "1230", "1330", "Return to Osaka", "Osaka, Japan")
ev("20261126", "1330", "1600", "Train, cable car and bus to Koyasan", "Gokurakubashi Station, Koya, Ito District, Wakayama, Japan",
   "About 90 min by train, then cable car and bus.")
ev("20261126", "1600", "1630", "Check in: Fugen In Temple", "FUGEN")
ev("20261126", "1730", "1830", "Vegetarian temple dinner (included)", "FUGEN")

# D12 Fri 27 Nov
ev("20261127", "0630", "0715", "Morning prayers with the monks", "FUGEN", "Time set by the temple. Dress warm.")
ev("20261127", "0715", "0800", "Temple breakfast (included)", "FUGEN")
ev("20261127", "0815", "0945", "Danjo Garan", "Danjo Garan, 152 Koyasan, Koya, Ito District, Wakayama, Japan")
ev("20261127", "1030", "1500", "Travel: Koyasan to Hiroshima via Osaka", "Shin Osaka Station, Yodogawa Ward, Osaka, Japan",
   "Leave before lunch. Shinkansen Shin Osaka to Hiroshima about 90 min. Streetcar to the hotel.")
ev("20261127", "1500", "1530", "Check in: Hotel Kuretakeso Otemachi", "KURETAKE",
   "1 min walk from Chuden-mae streetcar stop.")
ev("20261127", "1545", "1745", "Guided Peace Memorial Park and Museum", "Hiroshima Peace Memorial Museum, 1-2 Nakajimacho, Naka Ward, Hiroshima 730-0811, Japan")

# D13 Sat 28 Nov
ev("20261128", "0730", "0830", "Breakfast (included)", "KURETAKE")
ev("20261128", "0845", "1000", "Train and ferry to Miyajima", "Miyajimaguchi Ferry Terminal, Hatsukaichi, Hiroshima, Japan")
ev("20261128", "1000", "1230", "Great Torii, Itsukushima Shrine, Hall of 1,000 Mats", "Itsukushima Shrine, 1-1 Miyajimacho, Hatsukaichi, Hiroshima 739-0588, Japan",
   "Check the tide table for the torii.")
ev("20261128", "1230", "1600", "Free afternoon on Miyajima", "Miyajima, Hatsukaichi, Hiroshima, Japan")
ev("20261128", "1600", "1715", "Return to Hiroshima", "KURETAKE")
ev("20261128", "1900", "2130", "Final group evening", "Hiroshima, venue set by guide", "Meal not included.")

# D14 Sun 29 Nov
ev("20261129", "0700", "0800", "Breakfast (included) and check out", "KURETAKE",
   "Ask the guide for help with onward travel.")
ev("20261129", "0900", "0915", "Tour ends", "KURETAKE", "Tour finishes at 09:00 in Hiroshima.")
ev("20261129", "0915", "0945", "Peace Park river walk (optional)", "Atomic Bomb Dome, 1-10 Otemachi, Naka Ward, Hiroshima 730-0051, Japan",
   "Suggested in the operator PDF.")
ev("20261129", "0945", "1015", "Streetcar to Hiroshima Station", "Hiroshima Station, Minami Ward, Hiroshima, Japan")
ev("20261129", "1015", "1050", "Shinkansen: Hiroshima to Mihara", "MIHARA_STN",
   "Kodama about 25 min. JR Sanyo local takes about 75 min.")
ev("20261129", "1050", "1115", "Drop luggage: Super Hotel Mihara Ekimae", "SUPER",
   "Check in opens 15:00. Confirm they will hold bags.")
ev("20261129", "1130", "1215", "Bus to Buttsuji Temple", "JR Mihara Station, bus stop No. 4, Mihara, Hiroshima, Japan",
   "Geiyo Bus, about 40 min. Buses are infrequent. 2025 adult fare 730 yen.\n"
   "Extra autumn buses ran 15 to 30 Nov in 2025. Check the 2026 timetable. Taxi is the fallback.")
ev("20261129", "1215", "1500", "Buttsuji Temple autumn leaves", "Buttsuji Temple, 22 Motoyama, Takasaka-cho, Mihara, Hiroshima 729-0471, Japan",
   "Earlier research: autumn special opening runs to 29 Nov, 08:00 to 17:00, 500 yen. Reconfirm.\n"
   "Lenses: 24-70 for temple and foliage, 70-200 for compressed details.")
ev("20261129", "1500", "1545", "Bus back to Mihara Station", "MIHARA_STN",
   "Check the return times on arrival. 2025 timetable shows late afternoon buses.")
ev("20261129", "1545", "1600", "Check in: Super Hotel Mihara Ekimae", "SUPER", "Book the 05:50 taxi for tomorrow at reception.")
ev("20261129", "1615", "1745", "Mihara waterfront and castle ruins at dusk", "Mihara Castle Ruins Park, beside JR Mihara Station, Mihara, Hiroshima, Japan",
   "Sunset about 16:57. Blue hour on the harbour after.")
ev("20261129", "1800", "1930", "Dinner (self funded)", "Mihara, Hiroshima, Japan")

# D15 Mon 30 Nov
ev("20261130", "0550", "0610", "Taxi to Mount Fudekage (pre booked)", "SUPER",
   "Book the return trip in advance. Early taxis are not guaranteed.")
ev("20261130", "0610", "0745", "Mount Fudekage sunrise shoot", "Mt Fudekage Observatory, Mihara, Hiroshima, Japan (34.3759, 133.0815)",
   "Sunrise about 06:55. Summit about 311 m, Seto Inland Sea island layers, possible sea fog.\n"
   "Lenses: 24-70 and 70-200. Tripod if packed.")
ev("20261130", "0745", "0805", "Taxi back to hotel", "SUPER")
ev("20261130", "0815", "0930", "Breakfast (included) and pack", "SUPER")
ev("20261130", "0930", "1000", "Check out by 10:00, store luggage", "SUPER")
ev("20261130", "1000", "1315", "Free time in Mihara and lunch", "Mihara, Hiroshima, Japan")
ev("20261130", "1315", "1340", "Collect luggage, walk to station bus stop", "MIHARA_STN")
ev("20261130", "1350", "1428", "Airport bus: Mihara Station → Hiroshima Airport", "MIHARA_STN",
   "Not booked. Recheck the timetable and stop. Earlier research: 1,000 yen.\n"
   "The next bus (15:50) is too late for a safe margin.")
ev("20261130", "1430", "1530", "JAL check in and bag drop", "HIJ",
   "Both flights are on one booking. Ask to check the bag through to Sydney.")
ev("20261130", "1755", "1915", "✈ JL264 HIJ 17:55 → HND 19:15", "HIJ",
   "Japan Airlines JL264. Departure changed from 17:50 to 17:55.\n"
   "Gate A2 (app forecast). Arrives Haneda T1, gates 7 to 21. 1 h 20 min, 637 km.")
ev("20261130", "1915", "2030", "Haneda transfer: T1 to T3", "HND1",
   "Connection 2 h 45 min. Take the free inter terminal shuttle bus.\n"
   "International check in, security and emigration at T3.")
ev("20261130", "2200", "1000", "✈ QF60 HND 22:00 → SYD 10:00 (+1)", "HND3",
   "Qantas QF60. Haneda T3 to Sydney T1. Overnight, 10 h.\n"
   "Arrival changed from 09:55 to 10:00 Sydney time.", stz=TOK, etz=SYD, edate="20261201")

# ---------- ICS writer ----------
def esc(s):
    return (s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n"))

def fold(line):
    b = line.encode("utf-8")
    if len(b) <= 75:
        return line
    out, cur = [], b""
    limit = 75
    for ch in line:
        cb = ch.encode("utf-8")
        if len(cur) + len(cb) > limit:
            out.append(cur.decode("utf-8"))
            cur = b""
            limit = 74  # leading space on continuation
        cur += cb
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out)

VTZ = """BEGIN:VTIMEZONE
TZID:Asia/Tokyo
BEGIN:STANDARD
DTSTART:19700101T000000
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
TZNAME:JST
END:STANDARD
END:VTIMEZONE
BEGIN:VTIMEZONE
TZID:Australia/Sydney
BEGIN:STANDARD
DTSTART:19700405T030000
RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU
TZOFFSETFROM:+1100
TZOFFSETTO:+1000
TZNAME:AEST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19701004T020000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=1SU
TZOFFSETFROM:+1000
TZOFFSETTO:+1100
TZNAME:AEDT
END:DAYLIGHT
END:VTIMEZONE""".split("\n")

def next_day(d):
    from datetime import date, timedelta
    dt = date(int(d[:4]), int(d[4:6]), int(d[6:])) + timedelta(days=1)
    return dt.strftime("%Y%m%d")

lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//akumarau//Japan Trip 2026//EN",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Japan Trip 2026",
         "X-WR-TIMEZONE:Asia/Tokyo", "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"] + VTZ

n = 0
for d, title, loc, desc in ALLDAY:
    n += 1
    lines += ["BEGIN:VEVENT", f"UID:japan2026-allday-{d}@akumarau", f"DTSTAMP:{NOW}",
              f"DTSTART;VALUE=DATE:{d}", f"DTEND;VALUE=DATE:{next_day(d)}",
              f"SUMMARY:{esc(title)}", f"LOCATION:{esc(loc)}", f"DESCRIPTION:{esc(desc)}",
              "CATEGORIES:Japan Trip", "TRANSP:TRANSPARENT",
              "X-MICROSOFT-CDO-BUSYSTATUS:FREE", "X-MICROSOFT-CDO-ALLDAYEVENT:TRUE",
              "END:VEVENT"]

TZLABEL = {TOK: "Tokyo", SYD: "Sydney"}
for i, (d, s, e, title, loc, desc, stz, etz, ed) in enumerate(T, 1):
    if stz == etz:
        lt = f"Local time ({TZLABEL[stz]}): {s[:2]}:{s[2:]} to {e[:2]}:{e[2:]}"
    else:
        lt = f"Local time: {s[:2]}:{s[2:]} {TZLABEL[stz]} to {e[:2]}:{e[2:]} {TZLABEL[etz]}"
    full = lt + ("\n" + desc if desc else "")
    if "venue set by guide" in loc or "set by guide" in loc or (stz == TOK and "Flight" not in title and not title.startswith("✈")):
        pass
    lines += ["BEGIN:VEVENT", f"UID:japan2026-{d}-{s}-{i:03d}@akumarau", f"DTSTAMP:{NOW}",
              f"DTSTART;TZID={stz}:{d}T{s}00", f"DTEND;TZID={etz}:{ed}T{e}00",
              f"SUMMARY:{esc(title)}", f"LOCATION:{esc(loc)}", f"DESCRIPTION:{esc(full)}",
              "CATEGORIES:Japan Trip", "TRANSP:TRANSPARENT",
              "X-MICROSOFT-CDO-BUSYSTATUS:FREE", "END:VEVENT"]

lines.append("END:VCALENDAR")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "japan-2026.ics"), "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(fold(l) for l in lines) + "\r\n")
print(f"all day: {len(ALLDAY)}, timed: {len(T)}")
