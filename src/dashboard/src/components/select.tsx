/*
 * @Author: hibana2077 hibana2077@gmail.com
 * @Date: 2024-04-12 14:51:01
 * @LastEditors: hibana2077 hibana2077@gmail.com
 * @LastEditTime: 2024-04-12 14:55:20
 * @FilePath: \plant_knowledge_pipepline\src\dashboard\src\components\select.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import {
    Select,
    SelectItem,
  } from '@tremor/react';
  
  export function SelectHero() {
    return (
      <div className="mx-auto max-w-xs">
        <Select defaultValue="Single_page">
          <SelectItem value="Single_page">Single page</SelectItem>
          <SelectItem value="Recursive_page">Recursive page</SelectItem>
        </Select>
      </div>
    );
  }