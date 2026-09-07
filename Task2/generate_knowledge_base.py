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
    "01_Kaelen_Stormrider.md": """Kaelen Stormrider был могущественным Luminari, известным своим мастерством управления Aetherium. Родился на Dustfall, он был рабом, но позже стал героем Freedom Coalition. Его путь к тёмной стороне начался после видений гибели его возлюбленной, Queen Seraphine. В конце концов он превратился в Vorlag the Dread — самого жестокого полководца Imperium Dominus.""",
    "02_Vorlag_the_Dread.md": """Vorlag the Dread — тёмный лорд Shadow Cabal, бывший Luminari. Носит чёрный механический доспех и дышит с помощью респиратора. Он — правая рука Supreme Arbiter Malachor. Известен своей жестокостью и умением управлять Aetherium с помощью гнева. Его учеником был Orin Lightseeker, его собственный сын.""",
    "03_Orin_Lightseeker.md": """Orin Lightseeker — молодой фермер с Dustfall, который позже стал ключевой фигурой Freedom Coalition. Он уничтожил Void Engine, используя Aetherium и мастерство пилотирования Aegis Strike Fighter. После битвы он обучил новое поколение Luminari и отказался от власти, чтобы странствовать по галактике.""",
    "04_Senator_Elara_Voss.md": """Elara Voss — лидер Freedom Coalition, харизматичная дипломатка с Verdant Prime. Она организовала базу повстанцев на Jungle Haven и была спасена Orin'ом с Void Engine. После падения Imperium она стала первым канцлером новой Stellar Concord.""",
    "05_Captain_Rylan_Stark.md": """Rylan Stark — контрабандист и капитан корабля Shadow Runner. Сначала работал на Mogul the Slug, но позже присоединился к Freedom Coalition. Его циничный юмор и преданность друзьям сделали его легендой. Участвовал в Glacier Siege и Moonfall Engagement.""",
    "06_Gorrak_the_Mighty.md": """Gorrak — Ursan, верный друг Rylan'a. Высокий, покрытый шерстью, обладает огромной силой. Служит механиком и телохранителем на Shadow Runner. Участвовал во всех ключевых битвах повстанцев.""",
    "07_Master_Theron_Aldric.md": """Theron Aldric — старый Luminari, наставник Orin'а. Пережил Edict of Annihilation и скрывался на Dustfall. Научил Orin'а управлять Aetherium и передал ему Photon Blade. Пожертвовал собой, чтобы спасти своих учеников от Vorlag the Dread.""",
    "08_Elder_Zorrin.md": """Zorrin — мудрый Luminari-отшельник, живший на болотах Misty Marsh. Он обучал Orin'а секретам Aetherium и предсказал падение Imperium. Его слова: «Размер не имеет значения, важна воля».""",
    "09_Supreme_Arbiter_Malachor.md": """Malachor — верховный правитель Imperium Dominus, мастер Shadow Cabal. Интриган, который захватил власть через обман и убийства. Считал себя воплощением порядка. Был уничтожен Vorlag'ом в финальной битве на Verdant Moon.""",
    "10_Jaxx_the_Hunter.md": """Jaxx — наёмный убийца, работавший на Malachor'а. Носит потрёпанный плащ и всегда выполняет контракты. Пытался поймать Orin'а, но был побеждён. Позже стал независимым охотником за головами.""",
    "11_Dustfall.md": """Dustfall — пустынная планета с двумя солнцами. Домашний мир Orin'а и Kaelen'а. Здесь находился порт Port Scum — пристанище контрабандистов и преступников. Под поверхностью скрываются древние Luminari-руины.""",
    "12_Jungle_Haven.md": """Jungle Haven — планета, покрытая густыми джунглями. Служила главной базой Freedom Coalition. Здесь состоялась решающая битва, в результате которой был уничтожен Void Engine.""",
    "13_Glacier.md": """Glacier — ледяная планета, использовавшаяся как временное убежище повстанцев после потери Jungle Haven. Imperium нашла их с помощью зондов, что привело к Glacier Siege.""",
    "14_City-Core.md": """City-Core — столичная планета Imperium, покрытая мегаполисом высотой в сотни уровней. Здесь находился трон Malachor'а. После падения империи стала центром новой Stellar Concord.""",
    "15_Verdant_Prime.md": """Verdant Prime — цветущая планета, родной мир Elara Voss. Была разрушена Void Engine в демонстрационном акте. Это событие подтолкнуло многие миры к вступлению в Freedom Coalition.""",
    "16_Azure_Sphere.md": """Azure Sphere — водная планета, населённая амфибиями. Здесь Queen Seraphine правила до своего убийства. На планету вторглись силы Imperium, что вызвало войну.""",
    "17_Cinder.md": """Cinder — вулканическая планета, где Kaelen Stormrider превратился в Vorlag the Dread. Поверхность покрыта лавовыми реками и токсичной атмосферой. Здесь произошла дуэль между Master Kael и Vorlag'ом.""",
    "18_Misty_Marsh.md": """Misty Marsh — болотистая планета, скрытая от глаз Imperium. Здесь Elder Zorrin обучал Orin'а. Место полно опасных существ и древних тайн Aetherium.""",
    "19_Photon_Blade.md": """Photon Blade — энергетическое оружие Luminari и Shadow Cabal. Генерирует лезвие плазмы длиной около метра. Цвет зависит от кристалла внутри: синий (Luminari), красный (Shadow Cabal), зелёный (мастера), фиолетовый (редкость). Оружие может отражать выстрелы Ion Projector.""",
    "20_Void_Engine.md": """Void Engine — супероружие Imperium, станция размером с луну. Способна уничтожать целые планеты сфокусированным энергетическим лучом. Единственная уязвимость — тепловой реактор, доступ к которому возможен через узкий туннель. Уничтожена Orin'ом.""",
    "21_Ion_Projector.md": """Ion Projector — стандартное ручное оружие, стреляющее заряженными частицами. Используется как солдатами Imperium, так и повстанцами. Бывает разных модификаций: от пистолетов до тяжёлых винтовок.""",
    "22_Colossus_Walker.md": """Colossus Walker — четырёхногая боевая машина Imperium высотой 20 метров. Вооружена лазерными пушками. Уязвима для атак с воздуха и против пехоты, использующей канаты. Применялась в Glacier Siege.""",
    "23_Mechanoid.md": """Mechanoid — искусственный интеллект, используемый в роботах. Бывают боевые, обслуживающие и астромеханические. Некоторые обладают индивидуальностью и верностью хозяину.""",
    "24_Shadow_Runner.md": """Shadow Runner — модифицированный грузовой корабль, принадлежащий Rylan'у. Небольшой, юркий, способен развивать высокую скорость. Имеет скрытые отсеки для контрабанды. Участвовал в битвах на Jungle Haven и Verdant Moon.""",
    "25_Aegis_Strike_Fighter.md": """Aegis Strike Fighter — основной истребитель Freedom Coalition. Имеет четыре крыла, образующие крест. Маневренный, оснащён торпедами. Благодаря этому кораблю Orin удалось уничтожить Void Engine.""",
    "26_Onyx_Interceptor.md": """Onyx Interceptor — истребитель Imperium с двумя солнечными панелями. Скоростной, но слабо бронированный. Часто используется в массовых атаках.""",
    "27_Titan-class_Dreadnought.md": """Titan-class Dreadnought — линкор Imperium, длиной более километра. Вооружён десятками Ion Projector и способен нести штурмовые отряды. Являлся флагманом флота Malachor'а.""",
    "28_Luminari_Order.md": """Luminari Order — древний орден миротворцев, владеющих Aetherium. Они защищали Stellar Concord на протяжении тысячелетий. После Edict of Annihilation почти все были уничтожены, но выжившие возродили орден при Orin'е.""",
    "29_Shadow_Cabal.md": """Shadow Cabal — тайное общество, использующее тёмную сторону Aetherium. Стремятся к власти и контролю. Их глава — Supreme Arbiter Malachor. Они уничтожили Luminari Order и установили Imperium.""",
    "30_Ursan.md": """Ursan — раса высоких, волосатых гуманоидов с планеты Woodland. Обладают огромной силой, преданны друзьям. Легендарный Ursan — Gorrak the Mighty, друг Rylan'а.""",
    "31_Furling.md": """Furling — маленькая, пушистая раса с Verdant Moon. Живут в лесах и помогают Freedom Coalition в Moonfall Engagement. Их примитивное оружие (камни, луки) оказалось эффективным против Colossus Walkers.""",
    "32_Assault_on_Jungle_Haven.md": """Первая крупная победа Freedom Coalition. Используя тактику малых кораблей, повстанцы уничтожили Void Engine. Orin Lightseeker, управляя Aegis Strike Fighter, запустил торпеду в тепловой реактор, что вызвало цепную реакцию и уничтожило станцию.""",
    "33_Glacier_Siege.md": """Imperium атаковала базу повстанцев на Glacier. Битва шла в снегах, использовались Colossus Walkers. Freedom Coalition едва спаслась, но потеряла много бойцов. Это привело к временному отступлению на Verdant Moon.""",
    "34_Moonfall_Engagement.md": """Финальная битва на Verdant Moon. Orin сразился с Vorlag the Dread. Vorlag раскрыл, что он — отец Orin'а, и пожертвовал собой, чтобы убить Supreme Arbiter Malachor. В итоге Imperium пала, и была провозглашена новая Stellar Concord.""",
    "35_Edict_of_Annihilation.md": """Секретный приказ Supreme Arbiter Malachor уничтожить всех Luminari. Солдаты Imperium пошли по галактике, убивая Luminari и их учеников. Выжили лишь немногие, скрывавшиеся в отдалённых мирах."""
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