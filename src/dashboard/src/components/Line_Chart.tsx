/*
 * @Author: hibana2077 hibana2077@gmail.com
 * @Date: 2024-03-29 22:05:55
 * @LastEditors: hibana2077 hibana2077@gmail.com
 * @LastEditTime: 2024-04-11 12:04:57
 * @FilePath: \plant_knowledge_pipepline\src\dashboard\src\components\Line_Chart.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { LineChart } from '@tremor/react';

// need to connect to database to get the data
// ['Scheduled']

const chartdata = [
  {
    date: 'Jan 22',
    'Done Job': 2890,
    'Queue Job': 2338,
  },
  {
    date: 'Feb 22',
    'Done Job': 2756,
    'Queue Job': 2103,
  },
  {
    date: 'Mar 22',
    'Done Job': 3322,
    'Queue Job': 2194,
  },
  {
    date: 'Apr 22',
    'Done Job': 3470,
    'Queue Job': 2108,
  },
  {
    date: 'May 22',
    'Done Job': 3475,
    'Queue Job': 1812,
  },
  {
    date: 'Jun 22',
    'Done Job': 3129,
    'Queue Job': 1726,
  },
  {
    date: 'Jul 22',
    'Done Job': 3490,
    'Queue Job': 1982,
  },
  {
    date: 'Aug 22',
    'Done Job': 2903,
    'Queue Job': 2012,
  },
  {
    date: 'Sep 22',
    'Done Job': 2643,
    'Queue Job': 2342,
  },
  {
    date: 'Oct 22',
    'Done Job': 2837,
    'Queue Job': 2473,
  },
  {
    date: 'Nov 22',
    'Done Job': 2954,
    'Queue Job': 3848,
  },
  {
    date: 'Dec 22',
    'Done Job': 3239,
    'Queue Job': 3736,
  },
];

const dataFormatter = (number: number | bigint) =>
  `${Intl.NumberFormat('us').format(number).toString()}`;

export function LineChartHero() {
  return (
    <LineChart
      className="h-80"
      data={chartdata}
      index="date"
      categories={['Done Job', 'Queue Job']}
      colors={['indigo', 'rose']}
      valueFormatter={dataFormatter}
      yAxisWidth={60}
      onValueChange={(v) => console.log(v)}
    />
  );
}