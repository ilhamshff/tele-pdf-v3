# fileName : plugins/dm/Callback/pdfMetaData.py
# copyright ÂŠī¸ 2021 ilhamshff

import fitz
import time
import shutil
from pdf import PROCESS
from pyrogram import filters
from plugins.progress import progress
from pyrogram import Client as InHamePDF
from plugins.fileSize import get_size_format as gSF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#--------------->
#--------> LOCAL VARIABLES
#------------------->

pdfInfoMsg = """`Apa yang harus saya lakukan dengan file ini?`

File Name: `{}`
File Size: `{}`

`Nomer halaman: {}`âī¸"""

encryptedMsg = """`FILE IS ENCRYPTED` đ

File Name: `{}`
File Size: `{}`

`Nomer halaman: {}`âī¸"""

#--------------->
#--------> PDF META DATA
#------------------->

pdfInfo = filters.create(lambda _, __, query: query.data == "pdfInfo")
KpdfInfo = filters.create(lambda _, __, query: query.data.startswith("KpdfInfo"))

@InHamePDF.on_callback_query(pdfInfo)
async def _pdfInfo(bot, callbackQuery):
    try:
        # CHECKS PROCESS
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "Work in progress.. đ"
            )
            return
        # CB MESSAGE DELETES IF USER DELETED PDF
        try:
            fileExist=callbackQuery.message.reply_to_message.document.file_id
        except Exception:
            await bot.delete_messages(
                chat_id=callbackQuery.message.chat.id,
                message_ids=callbackQuery.message.message_id
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # DOWNLOADING STARTED
        downloadMessage=await callbackQuery.edit_message_text(
            "`Downloding your pdf..`âŗ",
        )
        pdf_path=f"{callbackQuery.message.message_id}/pdfInfo.pdf"
        file_id=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        # DOWNLOAD PROGRESS
        c_time=time.time()
        downloadLoc=await bot.download_media(
            message=file_id,
            file_name=pdf_path,
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        # CHECKS IS DOWNLOADING COMPLETED OR PROCESS CANCELED
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # OPEN FILE WITH FITZ
        with fitz.open(pdf_path) as pdf:
            isPdf=pdf.is_pdf
            metaData=pdf.metadata
            isEncrypted=pdf.is_encrypted
            number_of_pages=pdf.pageCount
            # CHECKS IF FILE ENCRYPTED
            if isPdf and isEncrypted:
                pdfMetaData=f"\nFile Encrypted đ\n"
            if isPdf and not(isEncrypted):
                pdfMetaData="\n"
            # ADD META DATA TO pdfMetaData STRING
            if metaData != None:
                for i in metaData:
                    if metaData[i] != "":
                        pdfMetaData += f"`{i}: {metaData[i]}`\n"
            fileName = callbackQuery.message.reply_to_message.document.file_name
            fileSize = callbackQuery.message.reply_to_message.document.file_size
            if isPdf and not(isEncrypted):
                editedPdfReplyCb=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("â­ METADATAâ­", callback_data=f"KpdfInfo|{number_of_pages}"),
                            InlineKeyboardButton("đŗī¸ PREVIEW đŗī¸", callback_data=f"Kpreview"),
                        ],[
                            InlineKeyboardButton("To Images đŧī¸", callback_data=f"KtoImage|{number_of_pages}"),
                            InlineKeyboardButton("To Text âī¸", callback_data=f"KtoText|{number_of_pages}")
                        ],[
                            InlineKeyboardButton("Encrypt đ",callback_data=f"Kencrypt|{number_of_pages}"),
                            InlineKeyboardButton("Decrypt đ", callback_data=f"notEncrypted"
                            )
                        ],[
                            InlineKeyboardButton("Compress đī¸", callback_data=f"Kcompress"),
                            InlineKeyboardButton("Rotate đ¤¸", callback_data=f"Krotate|{number_of_pages}")
                        ],[
                            InlineKeyboardButton("Split âī¸", callback_data=f"Ksplit|{number_of_pages}"),
                            InlineKeyboardButton("Merge đ§Ŧ", callback_data="merge")
                        ],[
                            InlineKeyboardButton("Stamp âĸī¸", callback_data=f"Kstamp|{number_of_pages}"),
                            InlineKeyboardButton("Rename âī¸", callback_data="rename")
                        ],[
                            InlineKeyboardButton("đĢ TUTUP đĢ", callback_data="closeALL")
                        ]
                    ]
                )
                await callbackQuery.edit_message_text(
                    pdfInfoMsg.format(
                        fileName, await gSF(fileSize), number_of_pages
                    ) + pdfMetaData,
                    reply_markup=editedPdfReplyCb
                )
            elif isPdf and isEncrypted:
                await callbackQuery.edit_message_text(
                    encryptedMsg.format(
                        fileName, await gSF(fileSize), number_of_pages
                    ) + pdfMetaData,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("đ DECRYPT đ", callback_data="decrypt")
                            ],[
                                InlineKeyboardButton("đĢ TUTUP đĢ", callback_data="closeALL")
                            ]
                        ]
                    )
                )
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
    # EXCEPTION DURING FILE OPENING
    except Exception as e:
        try:
            await callbackQuery.edit_message_text(
                f"SOMETHING went WRONG.. đ\n\nERROR: {e}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("â Error in file â", callback_data = f"error")
                        ],[
                            InlineKeyboardButton("đĢ TUTUP đĢ", callback_data="closeALL")
                        ]
                    ]
                )
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass

@InHamePDF.on_callback_query(KpdfInfo)
async def _KpdfInfo(bot, callbackQuery):
    try:
        _, number_of_pages = callbackQuery.data.split("|")
        await bot.answer_callback_query(
            callbackQuery.id,
            text = f"Total {number_of_pages} pages đ",
            show_alert = True,
            cache_time = 0
        )
    except Exception:
        pass

#                                                                                              Telegram: @ilhamshff
