import {DataSkeleton} from "@/components/DataSlot";
export default function Loading(){return <main className="route-loading"><div className="loading-header"><DataSkeleton lines={2}/></div><div className="loading-grid"><DataSkeleton lines={5}/><DataSkeleton lines={5}/><DataSkeleton lines={5}/></div><DataSkeleton lines={7}/></main>}
