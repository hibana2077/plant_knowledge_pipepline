'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:30:43
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-04 23:19:14
FilePath: \plant_knowledge_pipepline\src\control_node\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")