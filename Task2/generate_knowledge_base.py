import json
import os
from pathlib import Path

TERMS_MAP = {
    "Anakin Skywalker": "Kaelen Stormrider",
    "Darth Vader": "Vorlag the Dread",
    "Luke Skywalker": "Orin Lightseeker",
    "Leia Organa": "Senator Elara Voss",
    "Han Solo": "Captain Rylan Stark",
    "Chewbacca": "Gorrak the Mighty",
    "Obi-Wan Kenobi": "Master Theron Aldric",
    "Yoda": "Elder Zorrin",
    "Emperor Palpatine": "Supreme Arbiter Malachor",
    "Boba Fett": "Jaxx the Hunter",
    "The Force": "Aetherium",
    "Jedi": "Luminari Order",
    "Sith": "Shadow Cabal",
    "Galactic Republic": "Stellar Concord",
    "Galactic Empire": "Imperium Dominus",
    "Rebel Alliance": "Freedom Coalition",
    "Death Star": "Void Engine",
    "Star Destroyer": "Titan-class Dreadnought",
    "Millennium Falcon": "Shadow Runner",
    "X-wing": "Aegis Strike Fighter",
    "TIE Fighter": "Onyx Interceptor",
    "AT-AT": "Colossus Walker",
    "Lightsaber": "Photon Blade",
    "Blaster": "Ion Projector",
    "Droid": "Mechanoid",
    "Tatooine": "Dustfall",
    "Alderaan": "Verdant Prime",
    "Hoth": "Glacier",
    "Endor": "Verdant Moon",
    "Yavin IV": "Jungle Haven",
    "Coruscant": "City-Core",
    "Mos Eisley": "Port Scum",
    "Jabba the Hutt": "Mogul the Slug",
    "Wookiee": "Ursan",
    "Ewok": "Furling",
    "Battle of Yavin": "Assault on Jungle Haven",
    "Battle of Hoth": "Glacier Siege",
    "Battle of Endor": "Moonfall Engagement",
    "Order 66": "Edict of Annihilation",
    "Darth Maul": "Zhar the Viper",
    "Qui-Gon Jinn": "Master Kael",
    "Padmé Amidala": "Queen Seraphine",
    "Mace Windu": "Judge Vex",
    "Dooku": "Count Malvorn",
    "General Grievous": "Warlord Krix",
    "Naboo": "Azure Sphere",
    "Geonosis": "Hive Rock",
    "Kamino": "Waveforge",
    "Mustafar": "Cinder",
    "Utapau": "Sinkhole World",
    "The Clone Wars": "The Replicant War",
    "Jango Fett": "Toren the First"
}

# ----- 2. Содержимое документов (уже с заменёнными терминами) -----
DOCS = {
    "01_Kaelen_Stormrider.md": """Kaelen Stormrider was a mighty Luminari, known for his mastery of Aetherium. Born on Dustfall, he was a slave but later became a hero of the Freedom Coalition. His path to the dark side began after visions of his beloved Queen Seraphine's death. Eventually he transformed into Vorlag the Dread — the most ruthless commander of Imperium Dominus.""",
    "02_Vorlag_the_Dread.md": """Vorlag the Dread — a dark lord of the Shadow Cabal, a former Luminari. He wears a black mechanical suit and breathes through a respirator. He is the right hand of Supreme Arbiter Malachor. Known for his cruelty and ability to wield Aetherium through anger. His apprentice was Orin Lightseeker, his own son.""",
    "03_Orin_Lightseeker.md": """Orin Lightseeker — a young farmer from Dustfall who later became a key figure of the Freedom Coalition. He destroyed the Void Engine using Aetherium and his piloting skills in an Aegis Strike Fighter. After the battle, he trained a new generation of Luminari and refused power to wander the galaxy.""",
    "04_Senator_Elara_Voss.md": """Elara Voss — leader of the Freedom Coalition, a charismatic diplomat from Verdant Prime. She organised the rebel base on Jungle Haven and was rescued by Orin from the Void Engine. After the fall of Imperium, she became the first chancellor of the new Stellar Concord.""",
    "05_Captain_Rylan_Stark.md": """Rylan Stark — smuggler and captain of the ship Shadow Runner. He initially worked for Mogul the Slug but later joined the Freedom Coalition. His cynical humour and loyalty to friends made him a legend. He participated in the Glacier Siege and the Moonfall Engagement.""",
    "06_Gorrak_the_Mighty.md": """Gorrak — an Ursan, Rylan's faithful friend. Tall, covered in fur, possesses immense strength. Serves as mechanic and bodyguard on the Shadow Runner. Took part in all key rebel battles.""",
    "07_Master_Theron_Aldric.md": """Theron Aldric — an old Luminari, Orin's mentor. Survived the Edict of Annihilation and hid on Dustfall. Taught Orin to control Aetherium and gave him the Photon Blade. Sacrificed himself to save his students from Vorlag the Dread.""",
    "08_Elder_Zorrin.md": """Zorrin — a wise Luminari hermit who lived in the swamps of Misty Marsh. He taught Orin the secrets of Aetherium and predicted the fall of Imperium. His words: "Size matters not, only will." """,
    "09_Supreme_Arbiter_Malachor.md": """Malachor — the supreme ruler of Imperium Dominus, a master of the Shadow Cabal. A schemer who seized power through deception and murder. Believed himself to be the embodiment of order. Was destroyed by Vorlag in the final battle on Verdant Moon.""",
    "10_Jaxx_the_Hunter.md": """Jaxx — a bounty hunter who worked for Malachor. Wears a tattered cloak and always fulfils contracts. Tried to capture Orin but was defeated. Later became an independent hunter.""",
    "11_Dustfall.md": """Dustfall — a desert planet with two suns. Home world of Orin and Kaelen. Here lies Port Scum — a haven for smugglers and criminals. Beneath the surface hide ancient Luminari ruins.""",
    "12_Jungle_Haven.md": """Jungle Haven — a planet covered in dense jungles. Served as the main base of the Freedom Coalition. Here took place the decisive battle that resulted in the destruction of the Void Engine.""",
    "13_Glacier.md": """Glacier — an ice planet used as a temporary rebel hideout after the loss of Jungle Haven. Imperium found them using probes, leading to the Glacier Siege.""",
    "14_City-Core.md": """City-Core — the capital planet of Imperium, covered by a mega‑city hundreds of levels high. Here stood Malachor's throne. After the empire fell, it became the centre of the new Stellar Concord.""",
    "15_Verdant_Prime.md": """Verdant Prime — a blooming planet, home world of Elara Voss. It was destroyed by the Void Engine as a demonstration. This event pushed many worlds to join the Freedom Coalition.""",
    "16_Azure_Sphere.md": """Azure Sphere — a water planet inhabited by amphibians. Here Queen Seraphine ruled until her assassination. Imperium forces invaded the planet, sparking war.""",
    "17_Cinder.md": """Cinder — a volcanic planet where Kaelen Stormrider became Vorlag the Dread. The surface is covered by lava rivers and a toxic atmosphere. Here took place the duel between Master Kael and Vorlag.""",
    "18_Misty_Marsh.md": """Misty Marsh — a swampy planet hidden from Imperium's eyes. Here Elder Zorrin taught Orin. The place is full of dangerous creatures and ancient Aetherium secrets.""",
    "19_Photon_Blade.md": """Photon Blade — an energy weapon of the Luminari and Shadow Cabal. Generates a plasma blade about one meter long. Colour depends on the internal crystal: blue (Luminari), red (Shadow Cabal), green (masters), purple (rare). The weapon can deflect Ion Projector shots.""",
    "20_Void_Engine.md": """Void Engine — a superweapon of Imperium, a moon‑sized station. Can destroy entire planets with a focused energy beam. Its only weakness is the thermal reactor, accessible through a narrow exhaust tunnel. Destroyed by Orin.""",
    "21_Ion_Projector.md": """Ion Projector — standard handheld weapon that fires charged particles. Used by both Imperium soldiers and rebels. Comes in various models: from pistols to heavy rifles.""",
    "22_Colossus_Walker.md": """Colossus Walker — a four‑legged battle machine of Imperium, 20 metres tall. Armed with laser cannons. Vulnerable to air attacks and infantry using cables. Was used in the Glacier Siege.""",
    "23_Mechanoid.md": """Mechanoid — artificial intelligence used in robots. They come in combat, service, and astromechanical varieties. Some possess individuality and loyalty to their owner.""",
    "24_Shadow_Runner.md": """Shadow Runner — a modified freighter owned by Rylan. Small, agile, capable of high speed. Has hidden compartments for smuggling. Participated in battles at Jungle Haven and Verdant Moon.""",
    "25_Aegis_Strike_Fighter.md": """Aegis Strike Fighter — the main starfighter of the Freedom Coalition. Has four wings forming a cross. Maneuverable and equipped with torpedoes. Thanks to this ship, Orin managed to destroy the Void Engine.""",
    "26_Onyx_Interceptor.md": """Onyx Interceptor — an Imperium starfighter with two solar panels. Fast but lightly armoured. Often used in mass attacks.""",
    "27_Titan-class_Dreadnought.md": """Titan‑class Dreadnought — an Imperium battleship over a kilometre long. Armed with dozens of Ion Projectors and capable of carrying assault troops. Served as the flagship of Malachor's fleet.""",
    "28_Luminari_Order.md": """Luminari Order — an ancient order of peacekeepers who wield Aetherium. They protected the Stellar Concord for millennia. After the Edict of Annihilation, almost all were destroyed, but survivors revived the order under Orin.""",
    "29_Shadow_Cabal.md": """Shadow Cabal — a secret society that uses the dark side of Aetherium. They seek power and control. Their leader is Supreme Arbiter Malachor. They destroyed the Luminari Order and established Imperium.""",
    "30_Ursan.md": """Ursan — a race of tall, hairy humanoids from the planet Woodland. Possess great strength and loyalty to friends. The legendary Ursan is Gorrak the Mighty, Rylan's friend.""",
    "31_Furling.md": """Furling — a small, furry race from Verdant Moon. They live in the forests and help the Freedom Coalition in the Moonfall Engagement. Their primitive weapons (stones, bows) proved effective against Colossus Walkers.""",
    "32_Assault_on_Jungle_Haven.md": """The first major victory of the Freedom Coalition. Using small‑craft tactics, the rebels destroyed the Void Engine. Orin Lightseeker, piloting an Aegis Strike Fighter, launched a torpedo into the thermal reactor, causing a chain reaction that destroyed the station.""",
    "33_Glacier_Siege.md": """Imperium attacked the rebel base on Glacier. The battle was fought in snow, with Colossus Walkers deployed. The Freedom Coalition barely escaped but lost many fighters. This led to a temporary retreat to Verdant Moon.""",
    "34_Moonfall_Engagement.md": """The final battle on Verdant Moon. Orin faced Vorlag the Dread. Vorlag revealed he was Orin's father and sacrificed himself to kill Supreme Arbiter Malachor. Ultimately Imperium fell, and a new Stellar Concord was proclaimed.""",
    "35_Edict_of_Annihilation.md": """A secret order from Supreme Arbiter Malachor to exterminate all Luminari. Imperium soldiers swept through the galaxy, killing Luminari and their apprentices. Only a few survived, hiding in distant worlds."""
}

def generate_knowledge_base():
    base_dir = Path("knowledge_base")
    base_dir.mkdir(exist_ok=True)

    for filename, content in DOCS.items():
        filepath = base_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✔ Создан {filename}")

    with open("terms_map.json", "w", encoding="utf-8") as f:
        json.dump(TERMS_MAP, f, indent=2, ensure_ascii=False)
    print("✔ Создан terms_map.json")

    readme_content = """# База знаний для RAG-бота (вымышленный мир)

Данная база создана на основе вселенной Star Wars с полной заменой ключевых терминов.
Содержит 35 документов в формате Markdown и словарь замен terms_map.json.

## Структура
- knowledge_base/ — все документы
- terms_map.json — соответствия оригинал → вымышленное название

## Использование
Используйте эти документы для индексации в FAISS или другой векторной БД.
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✔ Создан README.md")

    print("\n✅ База знаний успешно сгенерирована!")

if __name__ == "__main__":
    generate_knowledge_base()