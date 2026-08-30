class TrendService:
    labels = ((.25,"FAST_RISING"),(.08,"RISING"),(-.08,"STABLE"),(-10,"DECLINING"))
    def calculate(self, volumes: list[int]) -> dict:
        if len(volumes) < 2 or volumes[-2] == 0: return {"growth":0.0,"acceleration":0.0,"label":"STABLE"}
        growth=(volumes[-1]-volumes[-2])/volumes[-2]
        previous=(volumes[-2]-volumes[-3])/volumes[-3] if len(volumes)>2 and volumes[-3] else 0
        label=next(name for threshold,name in self.labels if growth>=threshold)
        return {"growth":round(growth,4),"acceleration":round(growth-previous,4),"label":label}
