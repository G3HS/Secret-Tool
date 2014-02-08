# -*- coding: utf-8 -*- 

import wx, os, ConfigParser, sys, traceback
from binascii import hexlify, unhexlify
from Button import *
from ExpandPokesOffsets import *
from rom_insertion_operations import *
from LZ77 import *

def RepointPokes(rom, NewNumberOfPokes, NewDexSize, RAMOffset, StartOffset, rom_id, ini):
    #-#-#-#
    with open(rom, "r+b") as rom:
        SUPERBACKUP = rom.read()
        try:    
            #Write JPAN's hack.
            with open(os.path.join("Resources","SBRTable.bin"), "rb") as table:
                NewBlockTable = table.read()
                rom.seek(0x3FEC94)
                rom.write(NewBlockTable)
            with open(os.path.join("Resources","SaveBlockRecycle.bin"), "rb") as SBR:
                JPANsSBR = SBR.read()
                rom.seek(StartOffset)
                rom.write(JPANsSBR)
            rom.seek(0xD991E)
            rom.write("\x38\x47")
            rom.seek(0xD995C)
            offset = hex(StartOffset+0x8000061).rstrip("L").lstrip("0x").zfill(8)
            offset = make_pointer(offset)
            offset = unhexlify(offset)
            rom.write(offset)
            rom.seek(0xD9EDC)
            offset = hex(StartOffset+0x8000001).rstrip("L").lstrip("0x").zfill(8)
            offset = make_pointer(offset)
            offset = unhexlify(offset)
            rom.write("\x00\x48\x00\x47"+offset)
            rom.seek(0x13b8c2)
            rom.write("\x1D\xE0")
            #Begin to follow Doesnt's tutorial
            ##Step 1: Write the seen/caught flags data.
            OrgNewDexSize = NewDexSize
            while NewDexSize % 8 != 0:
                NewDexSize += 1
            NeededFlagBytes = int(NewDexSize/8)
            #Seen Flags
            #----Writing Flag Changes
            SeenFlagsPoint = make_pointer(RAMOffset)
            SeenFlagsPoint = unhexlify(SeenFlagsPoint)
            rom.seek(0x104B10)
            rom.write(SeenFlagsPoint)
            rom.seek(0x104B00)
            rom.write("\x00"*4)
            #----Reading Flag Changes
            rom.seek(0x104B94)
            rom.write(SeenFlagsPoint)
            rom.seek(0x104B6A)
            rom.write("\x01\x1C\x00\x00")
            rom.seek(0x104B78)
            rom.write("\x1A\xE0")
            #Caught Flags
            #----Writing Flag Changes
            tmp = int(RAMOffset, 16)+NeededFlagBytes
            tmp = hex(tmp).rstrip("L").lstrip("0x").zfill(8)
            CaughtFlagsPoint = make_pointer(tmp)
            CaughtFlagsPoint = unhexlify(CaughtFlagsPoint)
            rom.seek(0x104B5C)
            rom.write(CaughtFlagsPoint)
            rom.seek(0x104B16)
            rom.write("\x00"*6)
            rom.seek(0x104B26)
            rom.write("\x16\xE0")
            #----Reading Flag Changes
            rom.seek(0x104BB8)
            rom.write(CaughtFlagsPoint)
            rom.seek(0x104BA2)
            rom.write("\x01\x1C\x00\x00")
            #Skip extra tables
            rom.seek(0x104B34)
            rom.write("\x0F\xE0")
            ##Step 2: Repoint Goddamn everything
            #Name table
            NamesTable = int(ini.get(rom_id, "PokeNames"),0)
            OriginalNumOfPokes = int(ini.get(rom_id, "NumberofPokes"), 0)
            NameLength = int(ini.get(rom_id, "PokeNamesLength"), 0)
            TEMP = "\xCE\xBF\xC7\xCA"
            while len(TEMP) < NameLength:
                TEMP += "\xFF"
            BADEGG = "\xBC\xBB\xBE\x00\xBF\xC1\xC1"
            while len(BADEGG) < NameLength:
                BADEGG += "\xFF"
            UNOWN = "\xCF\xC8\xC9\xD1\xC8"
            while len(UNOWN) < NameLength:
                UNOWN += "\xFF"
            rom.seek(NamesTable)
            Names = rom.read(NameLength*OriginalNumOfPokes)
            ##Fill table with FF
            rom.seek(NamesTable)
            rom.write("\xFF"*len(Names))
            ##Append the new names
            while len(Names)/NameLength < 439:
                Names += UNOWN
            Names += BADEGG
            for n in range(NewNumberOfPokes):
                Names += TEMP
            Names = "\xAC\xAC\xAC\xAC\xAC\xAC\xAC\xAC\xAC\xAC\xFF"+Names
            ##Write the names
            NewNamesOffset = FindFreeSpace(StartOffset, len(Names),rom)
            rom.seek(NewNamesOffset)
            rom.write(Names)        
            ##Write the pointers for the names
            NamesPointer = MakeByteStringPointer(NewNamesOffset)
            for offset in NameTablePointers:
                rom.seek(offset)
                rom.write(NamesPointer)
            ##Allow reading from new table.
            rom.seek(0x41000)
            rom.write("\x00"*6)
            #Base Stats Table
            basestatsoffset = int(ini.get(rom_id, "pokebasestats"), 0)
            basestatslength = int(ini.get(rom_id, "pokebasestatslength"), 0)
            BlankEntry = "\x00"*basestatslength
            rom.seek(basestatsoffset)
            BaseStats = rom.read(basestatslength*OriginalNumOfPokes)
            TotalPokesAfterChanges = 440+NewNumberOfPokes
            ##Fill old table with FF
            rom.seek(basestatsoffset)
            rom.write("\xFF"*len(BaseStats))
            ##Write the stats
            while len(BaseStats)/basestatslength < TotalPokesAfterChanges:
                BaseStats += BlankEntry
            NewStatsOffset = FindFreeSpace(StartOffset, len(BaseStats),rom)
            rom.seek(NewStatsOffset)
            rom.write(BaseStats)     
            ##Write the pointers for the names
            StatsPointer = MakeByteStringPointer(NewStatsOffset)
            for offset in StatsTablePointers:
                rom.seek(offset)
                rom.write(StatsPointer)
            #Level-up movepool table
            LearnedMovesTable = int(ini.get(rom_id, "LearnedMoves"), 0)
            rom.seek(LearnedMovesTable)
            LearnedMoves = rom.read(4*OriginalNumOfPokes)
            BlankMoveSet = LearnedMoves[:4]
            ##Fill old table with FF
            rom.seek(LearnedMovesTable)
            rom.write("\xFF"*len(LearnedMoves))
            ##Write the move table
            while len(LearnedMoves)/4 < TotalPokesAfterChanges:
                LearnedMoves += BlankMoveSet
            NewMovesOffset = FindFreeSpace(StartOffset, len(LearnedMoves),rom)
            rom.seek(NewMovesOffset)
            rom.write(LearnedMoves)     
            ##Write the pointers for the table
            MovesPointer = MakeByteStringPointer(NewMovesOffset)
            for offset in LevelUpMoveTablePointers:
                rom.seek(offset)
                rom.write(MovesPointer)
            #Prepare to expand sprites.
            ##Insert blank palettes and sprites for the new pokemon.
            ImageSize = (64*64)/2
            BlankImage = "\x00"*ImageSize
            BlankImage = LZCompress(BlankImage)
            BlankPalette = "\x00\x00"*16
            BlankPalette = LZCompress(BlankPalette)
            BlankImageOffset = FindFreeSpace(StartOffset, len(BlankImage),rom)
            rom.seek(BlankImageOffset)
            rom.write(BlankImage)
            BlankPaletteOffset = FindFreeSpace(StartOffset, len(BlankPalette),rom)
            rom.seek(BlankPaletteOffset)
            rom.write(BlankPalette)
            BlankImagePointer = MakeByteStringPointer(BlankImageOffset)
            BlankPalettePointer = MakeByteStringPointer(BlankPaletteOffset)
            NewImageEntry = BlankImagePointer+"\x00\x08\x00\x00"
            NewPaletteEntry = BlankPalettePointer+"\x00\x00\x00\x00"
            frontspritetable = int(ini.get(rom_id, "frontspritetable"), 0)
            backspritetable = int(ini.get(rom_id, "backspritetable"), 0)
            frontpalettetable = int(ini.get(rom_id, "frontpalettetable"), 0)
            shinypalettetable = int(ini.get(rom_id, "shinypalettetable"), 0)
            #Extend Sprite Tables
            #-Front Sprite Table
            rom.seek(frontspritetable)
            FrontSprites = rom.read(8*440)
            ##Fill old table with FF
            rom.seek(frontspritetable)
            rom.write("\xFF"*len(FrontSprites))
            ##Write the sprite table
            while len(FrontSprites)/8 < TotalPokesAfterChanges:
                FrontSprites += NewImageEntry
            NewFSOffset = FindFreeSpace(StartOffset, len(FrontSprites),rom)
            rom.seek(NewFSOffset)
            rom.write(FrontSprites)     
            ##Write the pointers for the table
            FSPointer = MakeByteStringPointer(NewFSOffset)
            for offset in FrontSpriteTablePointers:
                rom.seek(offset)
                rom.write(FSPointer)
            #Fix Oak intro
            TMP = NewFSOffset + 232
            TMPPointer = MakeByteStringPointer(TMP)
            rom.seek(0x130FA0)
            rom.write(TMPPointer)
            #-Back Sprite Table
            rom.seek(backspritetable)
            BackSprites = rom.read(8*440)
            ##Fill old table with FF
            rom.seek(backspritetable)
            rom.write("\xFF"*len(BackSprites))
            ##Write the sprite table
            while len(BackSprites)/8 < TotalPokesAfterChanges:
                BackSprites += NewImageEntry
            NewBSOffset = FindFreeSpace(StartOffset, len(BackSprites),rom)
            rom.seek(NewBSOffset)
            rom.write(BackSprites)     
            ##Write the pointers for the table
            BSPointer = MakeByteStringPointer(NewBSOffset)
            for offset in BackSpriteTablePointers:
                rom.seek(offset)
                rom.write(BSPointer)
            #Sprite Fixes
            ##Remove limits
            rom.seek(0xED72)
            rom.write("\x07\xE0")
            rom.seek(0xF1B6)
            rom.write("\x07\xE0")
            #-Normal Palette Table
            rom.seek(frontpalettetable)
            NormalPals = rom.read(8*440)
            ##Fill old table with FF
            rom.seek(frontpalettetable)
            rom.write("\xFF"*len(NormalPals))
            ##Write the palette table
            while len(NormalPals)/8 < TotalPokesAfterChanges:
                NormalPals += NewPaletteEntry
            NewNPalOffset = FindFreeSpace(StartOffset, len(NormalPals),rom)
            rom.seek(NewNPalOffset)
            rom.write(NormalPals)     
            ##Write the pointers for the table
            NPalPointer = MakeByteStringPointer(NewNPalOffset)
            for offset in FrontPaletteTablePointers:
                rom.seek(offset)
                rom.write(NPalPointer)
            #Fix bug with loading OAK
            TMP = NewNPalOffset + 232
            TMPPointer = MakeByteStringPointer(TMP)
            rom.seek(0x130fa4)
            rom.write(TMPPointer)
            #-Shiny Palette Table
            rom.seek(shinypalettetable)
            ShinyPals = rom.read(8*440)
            ##Fill old table with FF
            rom.seek(shinypalettetable)
            rom.write("\xFF"*len(ShinyPals))
            ##Write the palette table
            while len(ShinyPals)/8 < TotalPokesAfterChanges:
                ShinyPals += NewPaletteEntry
            NewSPalOffset = FindFreeSpace(StartOffset, len(ShinyPals),rom)
            rom.seek(NewSPalOffset)
            rom.write(ShinyPals)     
            ##Write the pointers for the table
            SPalPointer = MakeByteStringPointer(NewSPalOffset)
            for offset in ShinyPaletteTablePointers:
                rom.seek(offset)
                rom.write(SPalPointer)
            #Palette Fixes
            ##Remove limits
            rom.seek(0x44104)
            rom.write("\x04\xE0")
            #Player Y
            playerytable = int(ini.get(rom_id, "playerytable"), 0)
            rom.seek(playerytable)
            PlayerY = rom.read(4*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(playerytable)
            rom.write("\xFF"*len(PlayerY))
            ##Write the table
            while len(PlayerY)/4 < TotalPokesAfterChanges:
                PlayerY += "\x00\x00\x00\x00"
            NewPlayerYOffset = FindFreeSpace(StartOffset, len(PlayerY),rom)
            rom.seek(NewPlayerYOffset)
            rom.write(PlayerY)     
            ##Write the pointers for the table
            PlayerYPointer = MakeByteStringPointer(NewPlayerYOffset)
            for offset in PlayerYTablePointers:
                rom.seek(offset)
                rom.write(PlayerYPointer)
            #Enemy  Y
            enemyytable = int(ini.get(rom_id, "enemyytable"), 0)
            rom.seek(enemyytable)
            EnemyY = rom.read(4*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(enemyytable)
            rom.write("\xFF"*len(EnemyY))
            ##Write the table
            while len(EnemyY)/4 < TotalPokesAfterChanges:
                EnemyY += "\x00\x00\x00\x00"
            NewEnemyYOffset = FindFreeSpace(StartOffset, len(EnemyY),rom)
            rom.seek(NewEnemyYOffset)
            rom.write(EnemyY)     
            ##Write the pointers for the table
            EnemyYPointer = MakeByteStringPointer(NewEnemyYOffset)
            for offset in EnemyYTablePointers:
                rom.seek(offset)
                rom.write(EnemyYPointer)
            #Enemy Altitude
            enemyaltitudetable = int(ini.get(rom_id, "enemyaltitudetable"), 0)
            rom.seek(enemyaltitudetable)
            EnemyAlt = rom.read(OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(enemyaltitudetable)
            rom.write("\xFF"*len(EnemyAlt))
            ##Write the table
            while len(EnemyAlt) < TotalPokesAfterChanges:
                EnemyAlt += "\x00"
            NewEnemyAltOffset = FindFreeSpace(StartOffset, len(EnemyAlt),rom)
            rom.seek(NewEnemyAltOffset)
            rom.write(EnemyAlt)     
            ##Write the pointers for the table
            EnemyAltPointer = MakeByteStringPointer(NewEnemyAltOffset)
            for offset in EnemyAltTablePointers:
                rom.seek(offset)
                rom.write(EnemyAltPointer)
            #Change Position Limiters
            rom.seek(0x7472E)
            rom.write("\x03\xE0")
            rom.seek(0x7465E)
            rom.write("\x03\xE0")
            #IconPrep
            BlankIcon = "\x00"*((32*64)/2)
            BlankIconOffset = FindFreeSpace(StartOffset, len(BlankIcon),rom)
            BlankIconPointer = MakeByteStringPointer(BlankIconOffset)
            rom.seek(BlankIconOffset)
            rom.write(BlankIcon)
            #Icons
            iconspritetable = int(ini.get(rom_id, "iconspritetable"), 0)
            rom.seek(iconspritetable)
            Icons = rom.read(4*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(iconspritetable)
            rom.write("\xFF"*len(Icons))
            ##Write the icon table
            while len(Icons)/4 < TotalPokesAfterChanges:
                Icons += BlankIconPointer
            NewIconsOffset = FindFreeSpace(StartOffset, len(Icons),rom)
            rom.seek(NewIconsOffset)
            rom.write(Icons)     
            ##Write the pointers for the table
            IconsPointer = MakeByteStringPointer(NewIconsOffset)
            for offset in IconTablePointers:
                rom.seek(offset)
                rom.write(IconsPointer)
            #Icon Palettes
            iconpalettetable = int(ini.get(rom_id, "iconpalettetable"), 0)
            rom.seek(iconpalettetable)
            IconPals = rom.read(OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(iconpalettetable)
            rom.write("\xFF"*len(IconPals))
            ##Write the palette table
            while len(IconPals) < TotalPokesAfterChanges:
                IconPals += "\x00"
            NewIconPalsOffset = FindFreeSpace(StartOffset, len(IconPals),rom)
            rom.seek(NewIconPalsOffset)
            rom.write(IconPals)     
            ##Write the pointers for the table
            IconPalsPointer = MakeByteStringPointer(NewIconPalsOffset)
            for offset in IconPaletteTablePointers:
                rom.seek(offset)
                rom.write(IconPalsPointer)
            #Change Icon Limiters
            rom.seek(0x96F90)
            rom.write("\x00\x00")
            rom.seek(0x96E7A)
            rom.write("\x00\x00\x00\x00")
            rom.seek(0x971DA)
            rom.write("\x00\x00")
            #Step 3: Dealing with dex entries
            #Repoint the order table
            NationalDexOrder = int(ini.get(rom_id, "NationalDexOrder"), 0)
            numofnondexpokesafterchimecho = int(ini.get(rom_id, "numofnondexpokesafterchimecho"), 0)
            rom.seek(NationalDexOrder)
            NatDexOrder = rom.read(2*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(NationalDexOrder)
            rom.write("\xFF"*len(NatDexOrder))
            ##Write the table
            for n in range(numofnondexpokesafterchimecho):
                NatDexOrder += "\x00"
            i = 386
            while len(NatDexOrder)/2 < TotalPokesAfterChanges:
                i += 1
                tmp = hex(i).rstrip("L").lstrip("0x").zfill(4)
                tmp = unhexlify(tmp)[::-1]
                NatDexOrder += tmp
            NatDexOrderOffset = FindFreeSpace(StartOffset, len(NatDexOrder),rom)
            rom.seek(NatDexOrderOffset)
            rom.write(NatDexOrder)     
            ##Write the pointers for the table
            NatDexOrderPointer = MakeByteStringPointer(NatDexOrderOffset)
            for offset in NatDexOrderTablePointers:
                rom.seek(offset)
                rom.write(NatDexOrderPointer)
            #Now the actual dex table
            pokedex = int(ini.get(rom_id, "pokedex"), 0)
            LengthofPokedexEntry = int(ini.get(rom_id, "LengthofPokedexEntry"), 0)
            rom.seek(pokedex)
            DexEntries = rom.read(LengthofPokedexEntry*387)
            ##Fill old table with FF
            rom.seek(pokedex)
            rom.write("\xFF"*len(DexEntries))
            ##Write the table
            MissingnoEntry = DexEntries[:LengthofPokedexEntry]
            while len(DexEntries)/LengthofPokedexEntry < TotalPokesAfterChanges-numofnondexpokesafterchimecho:
                DexEntries += MissingnoEntry
            NewDexEntriesOffset = FindFreeSpace(StartOffset, len(DexEntries),rom)
            rom.seek(NewDexEntriesOffset)
            rom.write(DexEntries)     
            ##Write the pointers for the table
            NewDexEntriesPointer = MakeByteStringPointer(NewDexEntriesOffset)
            for offset in DexEntriesTablePointers:
                rom.seek(offset)
                rom.write(NewDexEntriesPointer)
            #CRUSH DEX LIMITERS
            if OrgNewDexSize < 510: #Number of dex entries < 510
                write = OrgNewDexSize/2
            elif OrgNewDexSize >= 510 and OrgNewDexSize < 1020:
                write = OrgNewDexSize/4
                rom.seek(0x1025EE)
                rom.write("\x40\x01")
            else:
                raise AttributeError("You have issues. {0} dex entries???? Really???".format(OrgNewDexSize))
            rom.seek(0x1025EC)
            write = hex(write).rstrip("L").lstrip("0x").zfill(2)
            write = unhexlify(write)[::-1]
            rom.write(write)
            
            DexMinusOne = OrgNewDexSize-1
            DexMinusOne = hex(DexMinusOne).rstrip("L").lstrip("0x").zfill(4)
            DexMinusOne = unhexlify(DexMinusOne)[::-1]
            rom.seek(0x103920)
            rom.write(DexMinusOne)
            
            rom.seek(0x43220)
            rom.write("\x00\x00")
            #Step 4: Misc. repointing
            rom.seek(0x88EA4)
            rom.write(DexMinusOne)
            rom.seek(0x104C28)
            rom.write(DexMinusOne)
            #Repoint TM Comp Table
            tmhmcompatibility = int(ini.get(rom_id, "tmhmcompatibility"), 0)
            TMHMEntryLength = int(ini.get(rom_id, "tmhmcompatibilitylength"), 0)
            rom.seek(tmhmcompatibility)
            TMHMData = rom.read(TMHMEntryLength*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(tmhmcompatibility)
            rom.write("\xFF"*len(TMHMData))
            ##Write the table
            BlankEntry = "\x00"*TMHMEntryLength
            while len(TMHMData)/TMHMEntryLength < TotalPokesAfterChanges:
                TMHMData += BlankEntry
            NewTMHMOffset = FindFreeSpace(StartOffset, len(TMHMData),rom)
            rom.seek(NewTMHMOffset)
            rom.write(TMHMData)     
            ##Write the pointers for the table
            NewTMHMPointer = MakeByteStringPointer(NewTMHMOffset)
            for offset in TMHMTablePointers:
                rom.seek(offset)
                rom.write(NewTMHMPointer)
            #Repoint Tutor Comp Table
            movetutorcomp = int(ini.get(rom_id, "movetutorcomp"), 0)
            movetutorcomplen = int(ini.get(rom_id, "movetutorcomplen"), 0)
            rom.seek(movetutorcomp)
            MoveTutorData = rom.read(movetutorcomplen*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(movetutorcomp)
            rom.write("\xFF"*len(MoveTutorData))
            ##Write the table
            BlankEntry = "\x00"*movetutorcomplen
            while len(MoveTutorData)/movetutorcomplen < TotalPokesAfterChanges:
                MoveTutorData += BlankEntry
            NewMoveTutorOffset = FindFreeSpace(StartOffset, len(MoveTutorData),rom)
            rom.seek(NewMoveTutorOffset)
            rom.write(MoveTutorData)     
            ##Write the pointers for the table
            NewMoveTutorPointer = MakeByteStringPointer(NewMoveTutorOffset)
            for offset in MoveTutorCompTablePointers:
                rom.seek(offset)
                rom.write(NewMoveTutorPointer)
            #Repoint Evolution Table
            evolutiontable = int(ini.get(rom_id, "evolutiontable"), 0)
            evolutionsperpoke = int(ini.get(rom_id, "evolutionsperpoke"), 0)
            lengthofoneentry = int(ini.get(rom_id, "lengthofoneentry"), 0)
            EvoDataLength = evolutionsperpoke*lengthofoneentry
            rom.seek(evolutiontable)
            EvoData = rom.read(EvoDataLength*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(evolutiontable)
            rom.write("\xFF"*len(EvoData))
            ##Write the table
            BlankEntry = "\x00"*EvoDataLength
            while len(EvoData)/EvoDataLength < TotalPokesAfterChanges:
                EvoData += BlankEntry
            NewEvoOffset = FindFreeSpace(StartOffset, len(EvoData),rom)
            rom.seek(NewEvoOffset)
            rom.write(EvoData)     
            ##Write the pointers for the table
            NewEvoPointer = MakeByteStringPointer(NewEvoOffset)
            for offset in EvoTablePointers:
                rom.seek(offset)
                rom.write(NewEvoPointer)
            #Repoint Item Animation Table
            ItemAnimationTable = int(ini.get(rom_id, "ItemAnimationTable"), 0)
            ItemAniTableEntLen = int(ini.get(rom_id, "ItemAnimationTableEntLen"), 0)
            rom.seek(ItemAnimationTable)
            ItemAniData = rom.read(ItemAniTableEntLen*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(ItemAnimationTable)
            rom.write("\xFF"*len(ItemAniData))
            ##Write the table
            BlankEntry = ItemAniData[ItemAniTableEntLen:ItemAniTableEntLen*2]
            while len(ItemAniData)/ItemAniTableEntLen < TotalPokesAfterChanges:
                ItemAniData += BlankEntry
            NewItemAniOffset = FindFreeSpace(StartOffset, len(ItemAniData),rom)
            rom.seek(NewItemAniOffset)
            rom.write(ItemAniData)     
            ##Write the pointers for the table
            NewItemAniPointer = MakeByteStringPointer(NewItemAniOffset)
            for offset in ItemAniTablePointers:
                rom.seek(offset)
                rom.write(NewItemAniPointer)
            #Fix Evolution Animation & Trainer Card Stamps
            rom.seek(0xEC9A)
            rom.write("\x07\xE0")
            rom.seek(0x97011)
            rom.write("\xE0")
            #Handle Cries
            HoennCryAuxTable = int(ini.get(rom_id, "HoennCryAuxTable"), 0)
            NumNewCries = NewNumberOfPokes+numofnondexpokesafterchimecho
            BackFill = "\x01\x00"*NumNewCries
            rom.seek(HoennCryAuxTable)
            AuxCryTableData = rom.read(0x10E)
            ##Fill old table with FF
            rom.seek(HoennCryAuxTable)
            rom.write("\xFF"*len(AuxCryTableData))
            ##Write the table
            AuxCryTableData += BackFill
            NewAuxCryOffset = FindFreeSpace(StartOffset, len(AuxCryTableData),rom)
            rom.seek(NewAuxCryOffset)
            rom.write(AuxCryTableData)     
            ##Write the pointers for the table
            NewAuxCryPointer = MakeByteStringPointer(NewAuxCryOffset)
            for offset in ItemAniTablePointers:
                rom.seek(offset)
                rom.write(NewAuxCryPointer)
            rom.seek(0x720CA)
            rom.write("\x01\x1C\x11\xE0")
            #Handle FootPrints
            FootPrints = int(ini.get(rom_id, "FootPrints"), 0)
            BlankFootPrint = "\x8C\x05\xD3\x08"
            rom.seek(FootPrints)
            FootPrintData = rom.read(4*OriginalNumOfPokes)
            ##Fill old table with FF
            rom.seek(FootPrints)
            rom.write("\xFF"*len(FootPrintData))
            ##Write the table
            while len(FootPrintData)/4 < TotalPokesAfterChanges:
                FootPrintData += BlankFootPrint
            NewFootPrintOffset = FindFreeSpace(StartOffset, len(FootPrintData),rom)
            rom.seek(NewFootPrintOffset)
            rom.write(FootPrintData)     
            ##Write the pointers for the table
            NewFootPrintPointer = MakeByteStringPointer(NewFootPrintOffset)
            for offset in FootPrintTablePointers:
                rom.seek(offset)
                rom.write(NewFootPrintPointer)
            #Step 5: Change the world.. I mean ini
            ini.set(rom_id, "PokeNames",hex(NewNamesOffset+11).rstrip("L"))
            ini.set(rom_id, "NumberofPokes", hex(TotalPokesAfterChanges).rstrip("L"))
            ini.set(rom_id, "pokebasestats", hex(NewStatsOffset).rstrip("L"))
            ini.set(rom_id, "LearnedMoves", hex(NewMovesOffset).rstrip("L"))
            ini.set(rom_id, "frontspritetable", hex(NewFSOffset).rstrip("L"))
            ini.set(rom_id, "backspritetable", hex(NewBSOffset).rstrip("L"))
            ini.set(rom_id, "frontpalettetable", hex(NewNPalOffset).rstrip("L"))
            ini.set(rom_id, "shinypalettetable", hex(NewSPalOffset).rstrip("L"))
            ini.set(rom_id, "playerytable", hex(NewPlayerYOffset).rstrip("L"))
            ini.set(rom_id, "enemyytable", hex(NewEnemyYOffset).rstrip("L"))
            ini.set(rom_id, "enemyaltitudetable", hex(NewEnemyAltOffset).rstrip("L"))
            ini.set(rom_id, "iconspritetable", hex(NewIconsOffset).rstrip("L"))
            ini.set(rom_id, "iconpalettetable", hex(NewIconPalsOffset).rstrip("L"))
            ini.set(rom_id, "NationalDexOrder", hex(NatDexOrderOffset).rstrip("L"))
            ini.set(rom_id, "pokedex", hex(NewDexEntriesOffset).rstrip("L"))
            ini.set(rom_id, "tmhmcompatibility", hex(NewTMHMOffset).rstrip("L"))
            ini.set(rom_id, "movetutorcomp", hex(NewMoveTutorOffset).rstrip("L"))
            ini.set(rom_id, "evolutiontable", hex(NewEvoOffset).rstrip("L"))
            ini.set(rom_id, "ItemAnimationTable", hex(NewItemAniOffset).rstrip("L"))
            ini.set(rom_id, "HoennCryAuxTable", hex(NewAuxCryOffset).rstrip("L"))
            ini.set(rom_id, "FootPrints", hex(NewFootPrintOffset).rstrip("L"))

            with open("PokeRoms.ini", "w") as PokeRomsIni:
                ini.write(PokeRomsIni)
        except Exception as Error:
            rom.seek(0)
            rom.write(SUPERBACKUP)
            TYPE, VALUE, TRACE = sys.exc_info()
            TraceList = traceback.format_tb(TRACE)
            sys.stderr.write("An error occurred while expanding the number of 'mons. Your rom has been restored to its previous state. Here is the traceback data:")
            for value in TraceList:
                sys.stderr.write(value)
            sys.stderr.write(TYPE)
            sys.stderr.write(VALUE)
def FindFreeSpace(starting, length, rom):
        search = "\xFF"*length
        rom.seek(0)
        read = rom.read()
        start = starting
        while True:
            offset = read.find(search, start)
            if offset == -1:
                return None
            if offset%4 != 0:
                start = offset+1
                continue
            if read[offset-1] != "\xFF":
                start = offset+1
                continue
            return offset
                    
class PokemonExpander(wx.Dialog):
    def __init__(self, rom, parent=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        
        self.offset = None
        self.rom = rom
        self.InitUI()
        self.SetTitle("'MON Expander")
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, "Welcome to the first ever 'mon expander. This tool will  take care of all of the heavy lifting.\n All the user has to do  is supply a start offset to begin searching for free  space. I did not\n set this program up to ask you for  every single offset because I felt it would be awfully\n boring. So, all you have to do is chose one offset and then sit back and relax and I will\n dynamically search  for free space after it and move any and all tables and expand them!\n:D ",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        Questions = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(Questions, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        QVboxA = wx.BoxSizer(wx.VERTICAL)
        QVboxB = wx.BoxSizer(wx.VERTICAL)
        Questions.Add(QVboxA, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        Questions.Add(QVboxB, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        
        txt = wx.StaticText(self, -1, "How many NEW 'mons would you like?",style=wx.TE_CENTRE)
        QVboxA.Add(txt, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        self.NewPokeNum = wx.SpinCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.NewPokeNum.SetRange(0,1020)
        self.NewPokeNum.Bind(wx.EVT_TEXT, self.GetOffset)
        QVboxA.Add(self.NewPokeNum, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        NumDexEntriesTxt = wx.StaticText(self, -1, "How many TOTAL 'dex entries would you like?",style=wx.TE_CENTRE)
        QVboxB.Add(NumDexEntriesTxt, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        self.NumDexEntries = wx.SpinCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.NumDexEntries.SetRange(0,1020)
        self.NumDexEntries.Bind(wx.EVT_TEXT, self.GetOffset)
        self.NumDexEntries.SetValue(387)
        QVboxB.Add(self.NumDexEntries, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        SEARCH = Button(self, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        txt2 = wx.StaticText(self, -1, "Please choose an offset to repoint to or specify a manual offset. If a manual offset is\nspecified, the list choice will be ignored.\n",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0,  wx.ALL | wx.ALIGN_CENTER, 5)
        
        self.OFFSETS = wx.ListBox(self, -1, size=(250,150))
        self.OFFSETS.Bind(wx.EVT_LISTBOX, self.GetOffset)
        vbox.Add(self.OFFSETS, 0,  wx.ALL | wx.ALIGN_CENTER, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(self, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.LEFT|wx.TOP|wx.BOTTOM| wx.ALIGN_CENTER, 5)
        self.MANUAL = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.MANUAL.Bind(wx.EVT_TEXT, self.GetOffset)
        hbox.Add(self.MANUAL, 0, wx.RIGHT|wx.TOP|wx.BOTTOM | wx.ALIGN_CENTER, 5)
        vbox.Add(hbox, 0, wx.ALL|wx.ALIGN_CENTER, 0)
        
        RAM_Head = wx.StaticText(self, -1, "\nPlease choose provide a RAM offset for the seen/caught flags.\nIf you don't know what this is, don't change it.\n",style=wx.TE_CENTRE)
        vbox.Add(RAM_Head, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        RAM_txt = wx.StaticText(self, -1, "RAM Offset: 0x",style=wx.TE_CENTRE)
        hbox2.Add(RAM_txt, 0, wx.LEFT|wx.TOP|wx.BOTTOM| wx.ALIGN_CENTER, 5)
        self.RAM = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.RAM.SetValue("0203c400")
        self.RAM.Bind(wx.EVT_TEXT, self.GetOffset)
        hbox2.Add(self.RAM, 0, wx.RIGHT|wx.TOP|wx.BOTTOM| wx.ALIGN_CENTER, 5)
        vbox.Add(hbox2, 0, wx.ALL|wx.ALIGN_CENTER, 0)
        
        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 10)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def GetOffset(self, *args):
        sel = self.OFFSETS.GetSelection()
        _offset_ = self.MANUAL.GetValue()
        self.RAM_offset = self.RAM.GetValue()
        self.NewNumOfPokes = self.NewPokeNum.GetValue()
        self.NewNumOfDexEntries = self.NumDexEntries.GetValue()
        if self.RAM_offset == "":
            self.RAM_offset = "0203c400"
        if _offset_ != "":
            if len(_offset_) > 6:
                check = _offset_[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                _offset_ = check+_offset_[-6:].zfill(6)
        elif sel != -1:
            _offset_ = self.OFFSETS.GetString(sel)[2:]
        else: return
        
        try: self.offset = int(_offset_, 16)
        except: return

    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.NewPokeNum.GetValue()*0x1C+"\xff"*27*0x1C
        with open(self.rom, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 0x720000
            for n in range(5):
                if x[1] == None:
                    break
                x = (0,True)
                while x[0] != 1:
                    offset = read.find(search, start)
                    if offset == -1:
                        x = (1,None)
                    if offset%4 != 0:
                        start = offset+1
                        continue
                    if read[offset-1] != "\xFF":
                        start = offset+1
                        continue
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)