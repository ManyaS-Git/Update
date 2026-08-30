import {DatabaseZap} from "lucide-react";

type DataSlotProps={
  name:string;
  endpoint:string;
  hasData:boolean;
  children:React.ReactNode;
  emptyTitle?:string;
  emptyMessage?:string;
};

/** Reusable boundary for API-backed dashboard modules. */
export function DataSlot({name,endpoint,hasData,children,emptyTitle="Waiting for analysis",emptyMessage="This module will populate after the topic analysis endpoint returns data."}:DataSlotProps){
  return <div className="data-slot" data-slot={name} data-endpoint={endpoint} data-state={hasData?"ready":"empty"}>
    {hasData?children:<div className="data-empty" role="status"><DatabaseZap size={21}/><strong>{emptyTitle}</strong><p>{emptyMessage}</p><code>{endpoint}</code></div>}
  </div>
}

export function DataSkeleton({lines=3}:{lines?:number}){return <div className="data-skeleton" aria-label="Loading live analytics">{Array.from({length:lines},(_,i)=><i key={i}/>)}</div>}
