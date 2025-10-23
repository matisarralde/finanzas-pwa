"use client";

import React, { useState, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { format, subMonths, addMonths } from "date-fns";
import { es } from "date-fns/locale";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from "lucide-react";

function useMonthState() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentMonthParam = searchParams.get("month");

  const currentDate = useMemo(() => (currentMonthParam ? new Date(`${currentMonthParam}-02`) : new Date()), [currentMonthParam]);
  const currentMonthISO = format(currentDate, "yyyy-MM");

  const setMonth = (date: Date) => {
    const newMonth = format(date, "yyyy-MM");
    const newParams = new URLSearchParams(searchParams.toString());
    newParams.set("month", newMonth);
    router.push(`/dashboard?${newParams.toString()}`);
  };

  const nextMonth = () => setMonth(addMonths(currentDate, 1));
  const prevMonth = () => setMonth(subMonths(currentDate, 1));

  return { currentDate, currentMonthISO, setMonth, nextMonth, prevMonth };
}

export default function MonthSelector() {
  const { currentDate, setMonth, nextMonth, prevMonth } = useMonthState();
  const [popoverOpen, setPopoverOpen] = useState(false);
  const formattedMonth = format(currentDate, "MMMM yyyy", { locale: es });

  const handleDateSelect = (date?: Date) => {
    if (date) {
      setMonth(date);
      setPopoverOpen(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="icon" className="h-9 w-9" onClick={prevMonth} aria-label="Mes anterior">
        <ChevronLeft className="h-4 w-4" />
      </Button>

      <Popover open={popoverOpen} onOpenChange={setPopoverOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="w-[200px] justify-start text-left font-normal h-9">
            <CalendarIcon className="mr-2 h-4 w-4" />
            <span className="capitalize">{formattedMonth}</span>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-2" align="start">
          <Calendar mode="single" selected={currentDate} onSelect={handleDateSelect} captionLayout="dropdown-buttons" fromYear={2020} toYear={new Date().getFullYear() + 1} />
        </PopoverContent>
      </Popover>

      <Button variant="outline" size="icon" className="h-9 w-9" onClick={nextMonth} aria-label="Mes siguiente">
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}

