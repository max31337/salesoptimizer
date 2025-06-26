"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface PopoverProps {
  children: React.ReactNode
}

interface PopoverTriggerProps {
  asChild?: boolean
  children: React.ReactNode
  className?: string
}

interface PopoverContentProps {
  className?: string
  children: React.ReactNode
}

const PopoverContext = React.createContext<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}>({
  isOpen: false,
  setIsOpen: () => {}
})

const Popover = ({ children }: PopoverProps) => {
  const [isOpen, setIsOpen] = React.useState(false)
  
  const contextValue = React.useMemo(() => ({
    isOpen,
    setIsOpen
  }), [isOpen])
  
  return (
    <PopoverContext.Provider value={contextValue}>
      <div className="relative">
        {children}
      </div>
    </PopoverContext.Provider>
  )
}

const PopoverTrigger = React.forwardRef<HTMLButtonElement, PopoverTriggerProps>(
  ({ asChild, children, className, ...props }, ref) => {
    const { setIsOpen } = React.useContext(PopoverContext)
    
    const handleClick = React.useCallback(() => {
      setIsOpen(true)
    }, [setIsOpen])
    
    if (asChild && React.isValidElement(children)) {
      return React.cloneElement(children, {
        ...props,
        ref,
        onClick: handleClick,
        className: cn(className, children.props.className),
      } as any)
    }
    
    return (
      <button 
        ref={ref} 
        onClick={handleClick} 
        className={className}
        type="button"
        {...props}
      >
        {children}
      </button>
    )
  }
)
PopoverTrigger.displayName = "PopoverTrigger"

const PopoverContent = React.forwardRef<HTMLDivElement, PopoverContentProps>(
  ({ className, children, ...props }, ref) => {
    const { isOpen, setIsOpen } = React.useContext(PopoverContext)
    const contentRef = React.useRef<HTMLDivElement>(null)
    
    React.useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }
      
      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside)
        return () => {
          document.removeEventListener('mousedown', handleClickOutside)
        }
      }
    }, [isOpen, setIsOpen])
    
    React.useImperativeHandle(ref, () => contentRef.current!, [])
    
    if (!isOpen) return null
    
    return (
      <div
        ref={contentRef}
        className={cn(
          "absolute z-50 mt-2 rounded-md border bg-popover p-4 text-popover-foreground shadow-md",
          "min-w-[8rem] bg-white dark:bg-gray-950",
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
PopoverContent.displayName = "PopoverContent"

export { Popover, PopoverTrigger, PopoverContent }
