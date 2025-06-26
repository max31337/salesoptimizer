"use client"

import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export interface CalendarProps {
  mode?: "single"
  selected?: Date
  onSelect?: (date: Date | undefined) => void
  initialFocus?: boolean
  className?: string
}

const Calendar = React.forwardRef<HTMLDivElement, CalendarProps>(({
  mode = "single",
  selected,
  onSelect,
  initialFocus,
  className,
  ...props
}, ref) => {
  const [currentDate, setCurrentDate] = React.useState(() => selected || new Date())
  
  // Use useMemo to create a stable today value
  const today = React.useMemo(() => {
    const now = new Date()
    return {
      year: now.getFullYear(),
      month: now.getMonth(),
      date: now.getDate()
    }
  }, []) // Empty dependency array - only calculate once
  
  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  const firstDayOfWeek = firstDayOfMonth.getDay()
  const daysInMonth = lastDayOfMonth.getDate()
  
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ]
  
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
  
  const goToPreviousMonth = React.useCallback(() => {
    setCurrentDate(new Date(year, month - 1, 1))
  }, [year, month])
  
  const goToNextMonth = React.useCallback(() => {
    setCurrentDate(new Date(year, month + 1, 1))
  }, [year, month])
  
  const handleDateClick = React.useCallback((day: number) => {
    const newDate = new Date(year, month, day)
    onSelect?.(newDate)
  }, [year, month, onSelect])
  
  const isSelected = React.useCallback((day: number) => {
    if (!selected) return false
    const date = new Date(year, month, day)
    return (
      selected.getFullYear() === date.getFullYear() &&
      selected.getMonth() === date.getMonth() &&
      selected.getDate() === date.getDate()
    )
  }, [selected, year, month])
  
  const isToday = React.useCallback((day: number) => {
    return (
      today.year === year &&
      today.month === month &&
      today.date === day
    )
  }, [today, year, month])
  
  // Generate calendar days
  const days = React.useMemo(() => {
    const result = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfWeek; i++) {
      result.push(null)
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      result.push(day)
    }
    
    return result
  }, [firstDayOfWeek, daysInMonth])
  
  return (
    <div ref={ref} className={cn("p-3", className)} {...props}>
      <div className="flex justify-between items-center mb-4">
        <Button
          variant="outline"
          size="sm"
          onClick={goToPreviousMonth}
          className="h-7 w-7 p-0"
          type="button"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        
        <h2 className="text-sm font-medium">
          {monthNames[month]} {year}
        </h2>
        
        <Button
          variant="outline"
          size="sm"
          onClick={goToNextMonth}
          className="h-7 w-7 p-0"
          type="button"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map((dayName) => (
          <div
            key={dayName}
            className="h-8 w-8 flex items-center justify-center text-xs font-medium text-muted-foreground"
          >
            {dayName}
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => (
          <div key={index} className="h-8 w-8 flex items-center justify-center">
            {day && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDateClick(day)}
                type="button"
                className={cn(
                  "h-8 w-8 p-0 text-xs",
                  isSelected(day) && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground",
                  isToday(day) && !isSelected(day) && "bg-accent text-accent-foreground"
                )}
              >
                {day}
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
})

Calendar.displayName = "Calendar"

export { Calendar }
