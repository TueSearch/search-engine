import { VITE_FRONTEND_DOMAIN, VITE_FRONTEND_URL } from '@rhc/constants';
import { getShortedID } from '@rhc/shortURL';
import { Event } from '@rhc/types/supabaseTypes';
import { DateArray, EventAttributes, ReturnObject, createEvent, createEvents } from 'ics';

/**
 * The function transforms a given date into an array of year, month, and day, either as a timestamp or
 * as a date object, depending on whether the event is an all-day event or not.
 * @param {Date} date - The date parameter is a Date object representing the date and time of an event.
 * @param {boolean} isAllday - A boolean value indicating whether the event is an all-day event or not.
 *
 * @return {DateArray}  Date as an array
 */
export function transformDateToDateArray(date: Date, isAllday: boolean): DateArray {
  const dateArray = [];
  // if event is allday event just return the date (Y-m-d)
  dateArray.push(date.getUTCFullYear(), date.getUTCMonth() + 1, date.getUTCDate());
  if (!isAllday) {
    dateArray.push(date.getUTCHours(), date.getUTCMinutes());
  }
  return dateArray as DateArray;
}

/**
 * The function transforms an event object into an object with event attributes for ics generation.
 * @param {Event} event - an event object
 *
 * @return {EventAttributes} An event attributes opbject
 */
export function transformEventToEventAttributes(event: Event): EventAttributes {
  const shortId = getShortedID(event.id);

  return {
    title: event.name,
    description: event.description,
    location: event.location,
    productId: VITE_FRONTEND_DOMAIN,
    uid: `${shortId}@${VITE_FRONTEND_URL}`,
    recurrenceRule: event.repeating && event.repetitionRRule ? event.repetitionRRule : undefined,
    start: transformDateToDateArray(event.startDate, event.allday),
    end: transformDateToDateArray(event.endDate, event.allday),
    url: `${VITE_FRONTEND_URL}/event/${shortId}`,
    created: transformDateToDateArray(event.createdAt, false),
    lastModified: event.updatedAt ? transformDateToDateArray(event.updatedAt, false) : undefined,
    calName: 'RHC Kalendar',
  };
}

/**
 * It takes an event object and returns an ICS object
 * @param {Event} event - Event
 * @return {ics.ReturnObject} An object with a .ics file.
 */
export function generateICSFromSingleEvent(event: Event): ReturnObject {
  const icsAttributes = transformEventToEventAttributes(event);
  return createEvent(icsAttributes);
}

/**
 * It takes an array of event objects and returns an ICS object
 * @param {Event[]} events - Array of events
 * @return {ics.ReturnObject} An object with a .ics file.
 */
export function generateICSFromMultipleEvents(events: Event[]): ReturnObject {
  const icsAttributes = events.map((event) => transformEventToEventAttributes(event));
  return createEvents(icsAttributes);
}

/**
 * This function downloads an ICS file by creating a blob and a URL object, and then creating a link
 * element with the appropriate attributes and clicking it.
 * @param {ReturnObject} ics - An ics return object
 *
 * @return {void}
 */
export function downloadICS(ics: ReturnObject): void {
  if (!ics.value) return;
  const blob = new Blob([ics.value], { type: 'text/calendar;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  console.log('url', url);
  link.setAttribute('href', url);
  link.setAttribute('download', 'calendar.ics');
  link.click();
}
