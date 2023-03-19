# import asyncio
# import json
# import os
# # from util.tasks import run_blocking_code
#
#
# # async def load_language_packs(base_language_folder: str, aiofiles=None) -> tuple(dict, list):
# #     """Create cache for language packs."""
# #     language_packs = {}
# #     languages = []
# #
# #     async def get_language_module_and_message():
# #         # get the modules and messages for each language
# #         for t_language in language_packs.values():
# #             await asyncio.sleep(0)  # bare yield
# #             for t_module in t_language.values():
# #                 for t_message_name in t_module.keys():
# #                     yield t_module, t_message_name
# #
# #     # load the json for every language to cache
# #     directories_result = await run_blocking_code(os.listdir, f"{base_language_folder}/")
# #     language_folders = [folder_name for folder_name in directories_result[0]
# #                              if os.path.isdir(f"{base_language_folder}/{folder_name}")]
# #     for folder_name in language_folders:
# #         await asyncio.sleep(0)  # bare yield
# #         languages.append(folder_name.lower())
# #         async with aiofiles.open(f"{base_language_folder}/{folder_name}/messages.json", encoding="UTF-8") \
# #                 as file:
# #             language_packs[folder_name.lower()] = json.loads(await file.read())
# #
# #     # make the content of all curly braces bolded in all available languages.
# #     async for module, message_name in get_language_module_and_message():
# #         await asyncio.sleep(0)  # bare yield
# #         module[message_name] = _apply_bold_to_braces(module[message_name])
#
#
# def _apply_bold_to_braces(text: str) -> str:
#     """Apply bold markdown in between braces."""
#     keywords_to_not_bold = [
#         "server_prefix", "bot_id", "support_server_link",
#     ]
#     for keyword in keywords_to_not_bold:
#         text = text.replace("{" + f"{keyword}" + "}", keyword)  # we do not want to bold these words
#
#     # bold the words
#     text = text.replace("{", "**{")
#     text = text.replace("}", "}**")
#
#     for keyword in keywords_to_not_bold:
#         text = text.replace(keyword, "{" + f"{keyword}" + "}")  # return the keywords back to their initial state.
#     return text
#
